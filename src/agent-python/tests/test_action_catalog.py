"""Le catalogue dérive du /openapi.json du script : transformation + robustesse."""
from agent import action_catalog


class _FakeResp:
    def __init__(self, payload, exc=None):
        self._payload = payload
        self._exc = exc

    def raise_for_status(self):
        if self._exc:
            raise self._exc

    def json(self):
        return self._payload


_OPENAPI = {
    "paths": {
        "/action/load_device/load_device": {
            "post": {
                "summary": "Load a device onto the selected track by name.",
                "requestBody": {
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {"name": {"type": "string"}},
                                "required": ["name"],
                            }
                        }
                    }
                },
            }
        },
        # Une route core (non /action/*) : ignorée par le catalogue keymapper.
        "/track/select": {"post": {"summary": "Select a track"}},
    }
}


def test_fetch_transforms_action_routes(monkeypatch):
    monkeypatch.setattr(action_catalog.requests, "get", lambda url, timeout: _FakeResp(_OPENAPI))
    catalog = action_catalog.fetch("http://script")
    assert len(catalog) == 1  # /track/select ignorée
    action = catalog[0]
    assert action["name"] == "load_device"
    assert action["label"] == "Load Device"  # méthode -> Title Case
    assert action["description"] == "Load a device onto the selected track by name."
    assert action["path"] == "/action/load_device/load_device"
    assert action["method"] == "POST"
    assert action["params"] == [{"name": "name", "type": "string", "required": True}]


def test_fetch_returns_empty_on_network_error(monkeypatch):
    import requests

    def _boom(url, timeout):
        raise requests.RequestException("down")

    monkeypatch.setattr(action_catalog.requests, "get", _boom)
    assert action_catalog.fetch("http://script") == []


def test_title_case():
    assert action_catalog._title_case("load_device") == "Load Device"
    assert action_catalog._title_case("hello") == "Hello"
