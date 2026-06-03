"""Tests de la lecture tolérante de runtime.json côté agent."""
import json
import os

from agent import runtime_state


def _set_appdata(monkeypatch, tmp_path):
    appdata = tmp_path / "AppData"
    (appdata / "Protocol0").mkdir(parents=True)
    monkeypatch.setenv("APPDATA", str(appdata))
    return os.path.join(str(appdata), "Protocol0", "runtime.json")


def test_read_missing_returns_none(monkeypatch, tmp_path):
    _set_appdata(monkeypatch, tmp_path)
    assert runtime_state.read() is None


def test_read_valid_payload(monkeypatch, tmp_path):
    path = _set_appdata(monkeypatch, tmp_path)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"script_url": "http://127.0.0.1:9123", "pid": 42, "version": "0.5.0"}, f)
    data = runtime_state.read()
    assert data is not None
    assert data["script_url"] == "http://127.0.0.1:9123"


def test_read_corrupt_returns_none(monkeypatch, tmp_path):
    path = _set_appdata(monkeypatch, tmp_path)
    with open(path, "w", encoding="utf-8") as f:
        f.write("{not valid json")
    assert runtime_state.read() is None


def test_read_missing_url_returns_none(monkeypatch, tmp_path):
    path = _set_appdata(monkeypatch, tmp_path)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"pid": 42}, f)
    assert runtime_state.read() is None


def test_read_empty_url_returns_none(monkeypatch, tmp_path):
    path = _set_appdata(monkeypatch, tmp_path)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"script_url": ""}, f)
    assert runtime_state.read() is None
