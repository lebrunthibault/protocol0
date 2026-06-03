"""Le listener ne doit déclencher qu'au front montant, pas sur l'auto-repeat clavier."""
from detector.config import Binding, ShortcutConfig
from detector.listener import ShortcutListener


class _FakeKey:
    """Imite une touche pynput : expose `vk` (touches alphanum) ou `name` (F-keys)."""

    def __init__(self, vk=None, name=None):
        self.vk = vk
        self.name = name


class _StubConfig(ShortcutConfig):
    def __init__(self, binding):
        self._binding = binding

    def reload_if_changed(self):
        return False

    def get(self, combo):
        return self._binding if combo == "u" else None


def _make_listener(monkeypatch, calls):
    # Ableton toujours "au premier plan" pour ne pas court-circuiter l'action.
    monkeypatch.setattr("detector.listener.ableton_is_foreground", lambda: True)
    binding = Binding(combo="u", action="load_device", params={"name": "Utility"})
    return ShortcutListener(_StubConfig(binding), lambda b: calls.append(b))


def test_autorepeat_fires_once(monkeypatch):
    calls = []
    listener = _make_listener(monkeypatch, calls)
    u = _FakeKey(vk=85)  # 'u'
    # Auto-repeat : plusieurs on_press sans release entre.
    listener._on_press(u)
    listener._on_press(u)
    listener._on_press(u)
    assert len(calls) == 1


def test_press_release_press_fires_twice(monkeypatch):
    calls = []
    listener = _make_listener(monkeypatch, calls)
    u = _FakeKey(vk=85)
    listener._on_press(u)
    listener._on_release(u)
    listener._on_press(u)
    assert len(calls) == 2


def test_distinct_keys_each_fire(monkeypatch):
    calls = []
    listener = _make_listener(monkeypatch, calls)
    # Deux objets distincts mais même vk -> même touche physique -> dédoublonnés.
    listener._on_press(_FakeKey(vk=85))
    listener._on_press(_FakeKey(vk=85))
    assert len(calls) == 1
