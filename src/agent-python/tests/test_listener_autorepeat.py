"""The listener's decision logic: rising-edge dispatch, per-event suppression, and
self-ignore of injected keys. Drives the pure `_decide()` seam directly (the ctypes
hook itself can't run in a unit test)."""
from agent.config import Binding, ShortcutConfig
from agent.listener import ShortcutListener

VK_U = 0x55          # 'u'
VK_E = 0x45          # 'e'
VK_T = 0x54          # 't'
VK_CTRL = 0x11       # VK_CONTROL


class _StubConfig(ShortcutConfig):
    def __init__(self, bindings):
        # bindings: dict combo -> Binding
        self._bindings = bindings

    def reload_if_changed(self):
        return False

    def get(self, combo):
        return self._bindings.get(combo)


def _make_listener(monkeypatch, calls, bindings=None, foreground=True):
    # _decide resolves letters via keymap.key_name_from_vk (ToUnicodeEx, layout/host
    # dependent). Pin it to a deterministic positional map so tests are stable across
    # keyboard layouts.
    names = {VK_U: "u", VK_E: "e", VK_T: "t"}
    monkeypatch.setattr("agent.listener.keymap.key_name_from_vk",
                        lambda vk, scan: names.get(vk))
    monkeypatch.setattr("agent.listener.ableton_is_foreground", lambda: foreground)
    if bindings is None:
        bindings = {"u": Binding(combo="u", action="load_device", params={"name": "Utility"})}
    listener = ShortcutListener(_StubConfig(bindings), lambda b, mods: calls.append((b, mods)))
    return listener


def _drain(listener):
    """Run the worker's job inline: _decide enqueues, the worker (not started in
    tests) would call on_action. Drain here so callbacks fire synchronously."""
    while not listener._queue.empty():
        binding, held = listener._queue.get_nowait()
        listener._on_action(binding, held)


def _down(listener, vk, scan=0, injected=False):
    r = listener._decide(vk, scan, is_down=True, injected=injected)
    _drain(listener)
    return r


def _up(listener, vk, scan=0, injected=False):
    return listener._decide(vk, scan, is_down=False, injected=injected)


def test_autorepeat_fires_once(monkeypatch):
    calls = []
    listener = _make_listener(monkeypatch, calls)
    # Auto-repeat: several key-downs with no release between.
    _down(listener, VK_U)
    _down(listener, VK_U)
    _down(listener, VK_U)
    assert len(calls) == 1


def test_press_release_press_fires_twice(monkeypatch):
    calls = []
    listener = _make_listener(monkeypatch, calls)
    _down(listener, VK_U)
    _up(listener, VK_U)
    _down(listener, VK_U)
    assert len(calls) == 2


def test_injected_events_are_ignored(monkeypatch):
    # Our own synthesized keys (guard / LLKHF_INJECTED) must not dispatch nor be tracked.
    calls = []
    listener = _make_listener(monkeypatch, calls)
    assert _down(listener, VK_U, injected=True) is False
    assert calls == []
    # A real keystroke (not injected) dispatches normally.
    _down(listener, VK_U)
    assert len(calls) == 1


def test_matched_combo_suppresses(monkeypatch):
    # A bound combo with Ableton foreground is swallowed (return True) and dispatched.
    calls = []
    listener = _make_listener(monkeypatch, calls)
    assert _down(listener, VK_U) is True
    assert len(calls) == 1


def test_unmatched_combo_passes(monkeypatch):
    # An unbound key is never suppressed and never dispatched.
    calls = []
    listener = _make_listener(monkeypatch, calls)
    assert _down(listener, VK_T) is False
    assert calls == []


def test_matched_but_not_foreground_passes(monkeypatch):
    # Bound combo but Ableton not foreground: don't steal the key from other apps.
    calls = []
    listener = _make_listener(monkeypatch, calls, foreground=False)
    assert _down(listener, VK_U) is False
    assert calls == []


def test_keyup_of_suppressed_down_is_suppressed(monkeypatch):
    # A suppressed down's matching up is also suppressed (balanced for Ableton).
    calls = []
    listener = _make_listener(monkeypatch, calls)
    assert _down(listener, VK_U) is True
    assert _up(listener, VK_U) is True
    # A subsequent unrelated up is not suppressed.
    assert _up(listener, VK_T) is False


def test_keyup_of_passed_down_is_not_suppressed(monkeypatch):
    calls = []
    listener = _make_listener(monkeypatch, calls)
    _down(listener, VK_T)        # unbound -> passed
    assert _up(listener, VK_T) is False


def test_autorepeat_of_suppressed_key_keeps_suppressing(monkeypatch):
    # Holding a bound trigger: repeats don't re-dispatch but must keep being swallowed
    # so they don't leak to Ableton.
    calls = []
    listener = _make_listener(monkeypatch, calls)
    assert _down(listener, VK_U) is True
    assert _down(listener, VK_U) is True   # repeat: still suppressed
    assert len(calls) == 1                 # but only one dispatch


def test_modifier_tracking_builds_combo(monkeypatch):
    # Holding ctrl then tapping 'e' resolves to the "ctrl+e" binding; the held-modifier
    # snapshot is passed to the callback.
    calls = []
    bindings = {"ctrl+e": Binding(combo="ctrl+e", action="send_keys", params={"keys": "ctrl+t"})}
    listener = _make_listener(monkeypatch, calls, bindings=bindings)
    assert _down(listener, VK_CTRL) is False     # modifier never suppressed
    assert _down(listener, VK_E) is True         # trigger suppressed
    assert len(calls) == 1
    binding, mods = calls[0]
    assert binding.params["keys"] == "ctrl+t"
    assert mods == {"ctrl"}
    # Releasing ctrl clears it from the tracked set.
    _up(listener, VK_CTRL)
    assert listener.held_modifiers() == set()


def test_modifiers_are_never_suppressed(monkeypatch):
    calls = []
    listener = _make_listener(monkeypatch, calls)
    assert _down(listener, VK_CTRL) is False
    assert _up(listener, VK_CTRL) is False
