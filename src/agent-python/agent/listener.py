"""Keyboard capture via a low-level Windows hook (WH_KEYBOARD_LL) -> combo
resolution -> action callback.

Unlike pynput's observe-only Listener, this owns the hook and controls its return
value per event, so it can SUPPRESS the trigger combo (return 1, skip
CallNextHookEx) and stop it from leaking to Ableton. pynput's Controller is still
used for injection (key_emitter), but capture is done here so the physical trigger
key never reaches the foreground app.

Architecture — decide synchronously, defer execution:
  - The hook proc runs synchronously inside a message pump on its own thread. Windows
    drops hooks whose callback is too slow, so the proc only DECIDES (suppress/pass)
    using cheap in-memory state and enqueues the matched binding.
  - A worker thread runs the actual action (injection / HTTP), off the hook thread.

All decision logic lives in the pure `_decide()` method (testable without a real
hook); the ctypes proc is a thin marshaller around it.

The canonical combo vocabulary (modifier order, key namespace) lives in `keymap`,
shared with the emitter so capture and injection stay in lock-step.
"""
import ctypes
import logging
import queue
import threading
from ctypes import wintypes
from typing import Optional, Set, Tuple

from agent import keymap
from agent.config import Binding, ShortcutConfig
from agent.foreground import ableton_is_foreground

logger = logging.getLogger("agent")

# --- Win32 low-level keyboard hook constants / types ---------------------------
_WH_KEYBOARD_LL = 13
_WM_KEYDOWN = 0x0100
_WM_KEYUP = 0x0101
_WM_SYSKEYDOWN = 0x0104  # fired (instead of WM_KEYDOWN) while Alt is held
_WM_SYSKEYUP = 0x0105
_WM_QUIT = 0x0012
_HC_ACTION = 0
_LLKHF_INJECTED = 0x10  # event was synthesized via SendInput (our own injection)

_DOWN_MESSAGES = (_WM_KEYDOWN, _WM_SYSKEYDOWN)

ULONG_PTR = ctypes.c_size_t
LRESULT = ctypes.c_ssize_t


class _KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("vkCode", wintypes.DWORD),
        ("scanCode", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


_HOOKPROC = ctypes.WINFUNCTYPE(LRESULT, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)

_user32 = ctypes.windll.user32
_kernel32 = ctypes.windll.kernel32

_user32.SetWindowsHookExW.restype = wintypes.HHOOK
_user32.SetWindowsHookExW.argtypes = (ctypes.c_int, _HOOKPROC, wintypes.HINSTANCE, wintypes.DWORD)
_user32.CallNextHookEx.restype = LRESULT
_user32.CallNextHookEx.argtypes = (wintypes.HHOOK, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)
_user32.UnhookWindowsHookEx.argtypes = (wintypes.HHOOK,)
_user32.GetMessageW.argtypes = (ctypes.c_void_p, wintypes.HWND, wintypes.UINT, wintypes.UINT)
_user32.PostThreadMessageW.argtypes = (
    wintypes.DWORD, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)


class ShortcutListener:
    def __init__(self, config: ShortcutConfig, on_action) -> None:
        self._config = config
        # on_action(binding, held_modifiers): held modifiers are snapshotted at
        # decision time and passed through so the worker doesn't read mutable state
        # late (the user may release a modifier between decision and injection).
        self._on_action = on_action
        self._pressed_modifiers: Set[str] = set()
        # Non-modifier keys currently held (by vk). Used to act on the rising edge
        # only: Windows repeats key-down while a key is held (auto-repeat), which
        # would fire the action multiple times for a single keystroke.
        self._held_keys: Set[int] = set()
        # vks whose key-down we suppressed, so we also suppress the matching key-up
        # (keeps down/up balanced for Ableton, which never saw the down).
        self._suppressed_down: Set[int] = set()

        self._queue: "queue.Queue[Optional[Tuple[Binding, Set[str]]]]" = queue.Queue()
        self._worker: Optional[threading.Thread] = None
        self._hook_thread: Optional[threading.Thread] = None
        self._hook = None  # HHOOK
        self._hook_tid: Optional[int] = None
        # Keep a strong ref to the ctypes callback: if it is GC'd while the hook is
        # installed, the process crashes (same lesson as single_instance).
        self._proc = _HOOKPROC(self._raw_proc)

    # --- lifecycle ------------------------------------------------------------
    def start(self) -> None:
        self._worker = threading.Thread(target=self._run_worker, daemon=True)
        self._worker.start()
        self._hook_thread = threading.Thread(target=self._run_hook, daemon=True)
        self._hook_thread.start()
        logger.info("keyboard listener started")

    def stop(self) -> None:
        if self._hook_tid is not None:
            _user32.PostThreadMessageW(self._hook_tid, _WM_QUIT, 0, 0)
        self._queue.put(None)  # unblock + terminate the worker
        for t in (self._hook_thread, self._worker):
            if t is not None:
                t.join(timeout=2.0)
        self._hook_thread = None
        self._worker = None

    def join(self) -> None:
        if self._hook_thread is not None:
            self._hook_thread.join()

    def held_modifiers(self):
        """Canonical modifiers currently physically held (ctrl/alt/shift/win)."""
        return set(self._pressed_modifiers)

    # --- hook thread ----------------------------------------------------------
    def _run_hook(self) -> None:
        self._hook_tid = _kernel32.GetCurrentThreadId()
        self._hook = _user32.SetWindowsHookExW(_WH_KEYBOARD_LL, self._proc, None, 0)
        if not self._hook:
            logger.error("SetWindowsHookExW failed (err %s)", ctypes.get_last_error())
            return
        # The hook only fires while this thread pumps messages. GetMessageW returns 0
        # on WM_QUIT (posted by stop()).
        msg = wintypes.MSG()
        while _user32.GetMessageW(ctypes.byref(msg), None, 0, 0) != 0:
            _user32.TranslateMessage(ctypes.byref(msg))
            _user32.DispatchMessageW(ctypes.byref(msg))
        _user32.UnhookWindowsHookEx(self._hook)
        self._hook = None

    def _raw_proc(self, nCode, wParam, lParam):
        """Thin ctypes marshaller: extract the event and ask _decide; never block."""
        if nCode == _HC_ACTION:
            try:
                kb = ctypes.cast(lParam, ctypes.POINTER(_KBDLLHOOKSTRUCT)).contents
                # Ignore our own injected keys: pynput's Controller emits via SendInput,
                # which Windows tags with LLKHF_INJECTED (verified on-device). This is
                # per-event and race-free, unlike a shared depth-counter guard.
                injected = bool(kb.flags & _LLKHF_INJECTED)
                is_down = wParam in _DOWN_MESSAGES
                if self._decide(kb.vkCode, kb.scanCode, is_down, injected):
                    return 1  # suppress: do NOT propagate to the foreground app
            except Exception as e:  # never let an exception escape into the hook
                logger.warning("hook proc error: %s", e)
        return _user32.CallNextHookEx(self._hook or 0, nCode, wParam, lParam)

    # --- pure decision logic (unit-tested directly) ---------------------------
    def _decide(self, vk: int, scan: int, is_down: bool, injected: bool) -> bool:
        """Update capture state and return True iff this event must be suppressed.

        Enqueues the matched binding (+ a held-modifier snapshot) as a side effect
        when a binding fires. Has no I/O except the config lookup (in-memory) and the
        foreground check (only on matched combos)."""
        if injected:
            # Our own synthesized keys: ignore entirely (don't re-trigger, don't track).
            return False

        mod = keymap.MODIFIER_VK.get(vk)
        if mod is not None:
            # Modifiers are tracked but never suppressed: the user's ctrl/alt must keep
            # working for everything else.
            if is_down:
                self._pressed_modifiers.add(mod)
            else:
                self._pressed_modifiers.discard(mod)
            return False

        if not is_down:
            self._held_keys.discard(vk)
            if vk in self._suppressed_down:
                self._suppressed_down.discard(vk)
                return True  # balance the suppressed down: swallow its up too
            return False

        # key-down. Auto-repeat: same vk still held -> don't re-dispatch, but keep
        # suppressing if we suppressed the original down.
        if vk in self._held_keys:
            return vk in self._suppressed_down
        self._held_keys.add(vk)

        name = keymap.key_name_from_vk(vk, scan)
        if name is None:
            return False
        combo = self._build_combo(name)
        self._config.reload_if_changed()
        binding = self._config.get(combo)
        if binding is None:
            return False
        if not ableton_is_foreground():
            logger.debug("combo %s ignored (Ableton not foreground)" % combo)
            return False
        logger.info("combo %s -> %s %s" % (combo, binding.action, binding.params))
        self._suppressed_down.add(vk)
        self._queue.put((binding, set(self._pressed_modifiers)))
        return True

    def _build_combo(self, key_name: str) -> str:
        mods = [m for m in keymap.MODIFIER_ORDER if m in self._pressed_modifiers]
        return "+".join(mods + [key_name])

    # --- worker thread --------------------------------------------------------
    def _run_worker(self) -> None:
        while True:
            item = self._queue.get()
            if item is None:
                return
            binding, held = item
            try:
                self._on_action(binding, held)
            except Exception as e:
                logger.warning("action %s failed: %s" % (binding.action, e))
