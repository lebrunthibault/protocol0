"""execute() est générique : il résout l'action dans le catalogue du script et POST."""
from agent import script_client
from agent.config import Binding
from agent.settings import Settings


def _client(monkeypatch, catalog, base_url="http://script"):
    c = script_client.ScriptClient(Settings())
    monkeypatch.setattr(c, "_resolve_base_url", lambda: base_url)
    monkeypatch.setattr(script_client.action_catalog, "fetch", lambda url, session=None: catalog)
    posted = {}
    monkeypatch.setattr(c, "_post", lambda base, path, body: posted.update(base=base, path=path, body=body))
    return c, posted


_LOAD_DEVICE = {
    "name": "load_device",
    "path": "/action/load_device/load_device",
    "method": "POST",
    "params": [{"name": "name", "type": "string", "required": True}],
}


def test_execute_posts_resolved_action(monkeypatch):
    c, posted = _client(monkeypatch, [_LOAD_DEVICE])
    c.execute(Binding(combo="u", action="load_device", params={"name": "Utility"}))
    assert posted["path"] == "/api/action/load_device/load_device"
    assert posted["body"] == {"name": "Utility"}


def test_execute_unknown_action_does_not_post(monkeypatch):
    c, posted = _client(monkeypatch, [_LOAD_DEVICE])
    c.execute(Binding(combo="u", action="nope", params={}))
    assert posted == {}


def test_execute_noop_when_script_down(monkeypatch):
    c = script_client.ScriptClient(Settings())
    monkeypatch.setattr(c, "_resolve_base_url", lambda: None)
    called = {"n": 0}
    monkeypatch.setattr(c, "_post", lambda *a, **k: called.update(n=called["n"] + 1))
    c.execute(Binding(combo="u", action="load_device", params={"name": "X"}))
    assert called["n"] == 0
