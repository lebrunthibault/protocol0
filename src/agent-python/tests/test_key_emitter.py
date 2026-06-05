"""Emitter: canonical combo -> key chord injection, with listener suppression."""
from agent import key_emitter


class _RecordingController:
    """Stand-in for pynput's Controller that records press/release order."""

    def __init__(self):
        self.events = []

    def press(self, key):
        self.events.append(("press", key))

    def release(self, key):
        self.events.append(("release", key))


def test_send_presses_modifiers_then_key_then_releases_reversed(monkeypatch):
    rec = _RecordingController()
    monkeypatch.setattr(key_emitter, "_controller", rec)
    key_emitter.send("ctrl+shift+n")
    kinds = [k for k, _ in rec.events]
    # press ctrl, press shift, press n, release n, release shift, release ctrl
    assert kinds == ["press", "press", "press", "release", "release", "release"]
    # main key 'n' is pressed third and released first (innermost).
    assert rec.events[2] == ("press", "n")
    assert rec.events[3] == ("release", "n")


def test_send_named_key(monkeypatch):
    rec = _RecordingController()
    monkeypatch.setattr(key_emitter, "_controller", rec)
    key_emitter.send("space")
    assert [k for k, _ in rec.events] == ["press", "release"]


def test_send_releases_then_restores_held_modifiers(monkeypatch):
    # L'utilisateur tient ctrl+alt et tape la touche trigger : on doit lever ses
    # modifiers, injecter le chord propre (ctrl+n), puis re-presser ctrl+alt.
    rec = _RecordingController()
    monkeypatch.setattr(key_emitter, "_controller", rec)
    from pynput import keyboard

    key_emitter.send("ctrl+n", held_modifiers=("ctrl", "alt"))

    ctrl = keyboard.Key.ctrl
    alt = keyboard.Key.alt
    # 1) lift held (ctrl, alt released first), 2) clean chord (press ctrl, press n,
    # release n, release ctrl), 3) restore held (press ctrl, press alt).
    assert rec.events == [
        ("release", ctrl),
        ("release", alt),
        ("press", ctrl),
        ("press", "n"),
        ("release", "n"),
        ("release", ctrl),
        ("press", ctrl),
        ("press", alt),
    ]


def test_send_no_held_modifiers_is_plain_chord(monkeypatch):
    rec = _RecordingController()
    monkeypatch.setattr(key_emitter, "_controller", rec)
    key_emitter.send("ctrl+n")
    assert [k for k, _ in rec.events] == ["press", "press", "release", "release"]


def test_send_unsupported_key_is_noop(monkeypatch):
    rec = _RecordingController()
    monkeypatch.setattr(key_emitter, "_controller", rec)
    key_emitter.send("ctrl+bogus")
    assert rec.events == []


def test_send_empty_combo_is_noop(monkeypatch):
    rec = _RecordingController()
    monkeypatch.setattr(key_emitter, "_controller", rec)
    key_emitter.send("")
    assert rec.events == []
