"""Canonical key vocabulary shared by the listener (capture) and the emitter (injection).

The canonical combo format is the contract between three places that MUST stay in
lock-step (proto spec, parity invariant):
  - the agent listener (capture), which matches on the physical `vk`;
  - the frontend capture (`useComboCapture.ts`), which matches on `event.code`;
  - the agent emitter (`key_emitter.py`), which turns a combo back into pynput keys.

Canonical form: lowercase, modifiers in the fixed order ctrl, alt, shift, win, then
the main key, joined by '+'. Ex. "ctrl+n", "ctrl+shift+f5", "ctrl+alt+space".

Namespace: a-z, 0-9, f1-f12, plus a set of named non-character keys (space, tab,
enter, esc, backspace, delete, arrows, home/end, page up/down). Named keys are needed
because most native Ableton shortcuts (transport, navigation) live outside a-z/0-9.
"""
import ctypes
from ctypes import wintypes

from pynput import keyboard

MODIFIER_ORDER = ["ctrl", "alt", "shift", "win"]

# Named (non-character) keys, canonical token -> pynput Key, used by the emitter to
# inject named keys (capture is done from raw vk codes via NAMED_VK below).
NAMED_TO_PYNPUT = {
    "space": keyboard.Key.space,
    "tab": keyboard.Key.tab,
    "enter": keyboard.Key.enter,
    "esc": keyboard.Key.esc,
    "backspace": keyboard.Key.backspace,
    "delete": keyboard.Key.delete,
    "up": keyboard.Key.up,
    "down": keyboard.Key.down,
    "left": keyboard.Key.left,
    "right": keyboard.Key.right,
    "home": keyboard.Key.home,
    "end": keyboard.Key.end,
    "pageup": keyboard.Key.page_up,
    "pagedown": keyboard.Key.page_down,
}

# ---------------------------------------------------------------------------
# vk-based vocabulary for the custom WH_KEYBOARD_LL hook (listener.py).
#
# The low-level hook delivers a virtual-key code + scan code, not a pynput Key
# object, so capture needs its own vk->token maps. Tokens stay identical to the
# canonical vocabulary (NAMED_TO_PYNPUT above, used for injection) so capture and
# injection remain in lock-step.
# ---------------------------------------------------------------------------

# Virtual-key code -> canonical modifier token. Generic + left/right variants all
# collapse to the same token (the canonical form has no left/right distinction).
MODIFIER_VK = {
    0x11: "ctrl",   # VK_CONTROL
    0xA2: "ctrl",   # VK_LCONTROL
    0xA3: "ctrl",   # VK_RCONTROL
    0x12: "alt",    # VK_MENU
    0xA4: "alt",    # VK_LMENU
    0xA5: "alt",    # VK_RMENU (AltGr -> alt, mirrors alt_gr handling)
    0x10: "shift",  # VK_SHIFT
    0xA0: "shift",  # VK_LSHIFT
    0xA1: "shift",  # VK_RSHIFT
    0x5B: "win",    # VK_LWIN
    0x5C: "win",    # VK_RWIN
}

# Virtual-key code -> canonical named-key token. Same namespace as NAMED_TO_PYNPUT,
# keyed by vk instead of pynput Key. F1-F12 (0x70-0x7B) are handled in key_name_from_vk.
NAMED_VK = {
    0x20: "space",     # VK_SPACE
    0x09: "tab",       # VK_TAB
    0x0D: "enter",     # VK_RETURN
    0x1B: "esc",       # VK_ESCAPE
    0x08: "backspace",  # VK_BACK
    0x2E: "delete",    # VK_DELETE
    0x26: "up",        # VK_UP
    0x28: "down",      # VK_DOWN
    0x25: "left",      # VK_LEFT
    0x27: "right",     # VK_RIGHT
    0x24: "home",      # VK_HOME
    0x23: "end",       # VK_END
    0x21: "pageup",    # VK_PRIOR
    0x22: "pagedown",  # VK_NEXT
}

_user32 = ctypes.windll.user32 if hasattr(ctypes, "windll") else None


def _layout_letter(vk: int, scan: int):
    """Layout-aware unmodified letter for a physical key via ToUnicodeEx.

    Translates against a ZEROED key-state buffer so no held modifier influences the
    result: Ctrl+E yields 'e' (not '\\x05'), and AltGr letters don't turn into
    punctuation. Returns a lowercase 'a'..'z' or None (not a single letter / call
    failed). This mirrors what pynput's `canonical()` does, but from the raw vk/scan
    the hook gives us instead of a pynput Key.
    """
    if _user32 is None:
        return None
    try:
        layout = _user32.GetKeyboardLayout(0)
        state = (ctypes.c_ubyte * 256)()  # all zero -> no modifiers active
        buf = ctypes.create_unicode_buffer(8)
        # ToUnicodeEx(vk, scan, keyState, buf, bufLen, flags, layout)
        n = _user32.ToUnicodeEx(
            wintypes.UINT(vk),
            wintypes.UINT(scan),
            state,
            buf,
            len(buf),
            0,
            layout,
        )
    except Exception:
        return None
    if n == 1:
        ch = buf[0].lower()
        # Only ASCII a-z: digits, punctuation and dead-key/accented results fall
        # through to positional mapping (the canonical letter namespace is a-z).
        if "a" <= ch <= "z":
            return ch
    return None


def key_name_from_vk(vk: int, scan: int):
    """Canonical name of a non-modifier key from its virtual-key + scan code.

    Layout-aware for letters (Q -> "q" on AZERTY) via ToUnicodeEx; positional for
    everything else (digits, numpad, function keys, named keys). Returns None if the
    key is outside the canonical namespace.
    """
    letter = _layout_letter(vk, scan)
    if letter is not None:
        return letter
    if 0x70 <= vk <= 0x7B:  # VK_F1..VK_F12
        return "f%d" % (vk - 0x6F)
    if 0x30 <= vk <= 0x39:  # '0'..'9' top row
        return chr(vk)
    if 0x60 <= vk <= 0x69:  # numpad 0..9
        return chr(vk - 0x30)
    named = NAMED_VK.get(vk)
    if named is not None:
        return named
    if 0x41 <= vk <= 0x5A:  # A-Z positional fallback (ToUnicodeEx unavailable)
        return chr(vk + 0x20)
    return None
