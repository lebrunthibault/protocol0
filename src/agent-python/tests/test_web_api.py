"""Tests de l'API web de l'agent (dispatch /api/* + /status, et le store shortcuts)."""
import json

import pytest

from agent.web import api


@pytest.fixture(autouse=True)
def _isolated_appdata(tmp_path, monkeypatch):
    # shortcut_store écrit sous %APPDATA%\Protocol0 : on isole sur un tmp.
    monkeypatch.setenv("APPDATA", str(tmp_path))


def _json(resp):
    code, body, ctype = resp
    assert "application/json" in ctype
    return code, json.loads(body)


def test_actions_catalog_empty_when_script_down(monkeypatch):
    # Script injoignable (pas de runtime.json) -> catalogue vide, jamais d'exception.
    monkeypatch.setattr("agent.web.api.runtime_state.read", lambda: None)
    code, data = _json(api.handle("GET", "/api/actions", "", b""))
    assert code == 200 and data == []


def test_actions_catalog_proxies_script(monkeypatch):
    # Script up -> /api/actions dérive le catalogue du /openapi.json du script.
    monkeypatch.setattr(
        "agent.web.api.runtime_state.read", lambda: {"script_url": "http://x"}
    )
    monkeypatch.setattr(
        "agent.web.api.action_catalog.fetch",
        lambda url: [{"name": "load_device", "label": "Load Device", "params": []}],
    )
    code, data = _json(api.handle("GET", "/api/actions", "", b""))
    assert code == 200
    assert data[0]["name"] == "load_device"
    assert data[0]["label"] == "Load Device"


def test_add_list_delete_roundtrip():
    payload = json.dumps(
        {"combo": "ctrl+alt+e", "action": "load_device", "params": {"name": "EQ Eight"}}
    ).encode()
    code, data = _json(api.handle("POST", "/api/shortcuts/add", "", payload))
    assert code == 200
    assert data == [{"combo": "ctrl+alt+e", "action": "load_device", "params": {"name": "EQ Eight"}}]

    code, data = _json(api.handle("GET", "/api/shortcuts", "", b""))
    assert len(data) == 1 and data[0]["combo"] == "ctrl+alt+e"

    code, data = _json(api.handle("POST", "/api/shortcuts/delete", "", json.dumps({"combo": "ctrl+alt+e"}).encode()))
    assert code == 200 and data == []


def test_upsert_replaces_same_combo():
    add = lambda action: api.handle(  # noqa: E731
        "POST",
        "/api/shortcuts/add",
        "",
        json.dumps({"combo": "alt+l", "action": action, "params": {}}).encode(),
    )
    add("load_device")
    _, data = _json(add("load_device"))
    # même combo -> une seule entrée (upsert par combo)
    assert len(data) == 1


def test_add_requires_combo_and_action():
    code, data = _json(api.handle("POST", "/api/shortcuts/add", "", b"{}"))
    assert code == 400 and "error" in data


def test_get_mutation_with_query_params():
    # mutations acceptées en GET aussi ; params = blob JSON url-décodé.
    q = "combo=ctrl%2Bk&action=load_device&params=%7B%22name%22%3A%22Reverb%22%7D"
    code, data = _json(api.handle("GET", "/api/shortcuts/add", q, b""))
    assert code == 200
    assert data[0] == {"combo": "ctrl+k", "action": "load_device", "params": {"name": "Reverb"}}


def test_ableton_shortcuts_catalog():
    code, data = _json(api.handle("GET", "/api/ableton-shortcuts", "", b""))
    assert code == 200
    assert "doc_url" in data and data["doc_url"].startswith("https://www.ableton.com")
    assert isinstance(data["shortcuts"], list) and data["shortcuts"]
    entry = data["shortcuts"][0]
    assert {"name", "label", "category", "keys"} <= set(entry)


def test_send_keys_binding_roundtrip():
    payload = json.dumps(
        {
            "combo": "ctrl+alt+q",
            "action": "send_keys",
            "params": {"keys": "ctrl+n", "label": "New Live Set"},
        }
    ).encode()
    code, data = _json(api.handle("POST", "/api/shortcuts/add", "", payload))
    assert code == 200
    assert data[0]["action"] == "send_keys"
    assert data[0]["params"]["keys"] == "ctrl+n"


def test_health_reports_version():
    code, data = _json(api.handle("GET", "/api/health", "", b""))
    assert code == 200 and data["ok"] is True and "version" in data


def test_unknown_api_path_is_404():
    code, _ = _json(api.handle("GET", "/api/nope", "", b""))
    assert code == 404


def test_non_api_path_falls_through_to_static():
    # un chemin non-API renvoie None -> le serveur tentera les fichiers statiques.
    assert api.handle("GET", "/shortcuts", "", b"") is None
    assert api.handle("GET", "/", "", b"") is None
