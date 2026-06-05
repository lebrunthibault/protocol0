"""Tests du service de fichiers statiques de la SPA (résolution + catch-all + anti-traversal)."""
import importlib

from agent.web import static_files


def _build_fake_dist(tmp_path, monkeypatch):
    dist = tmp_path / "frontend" / "dist"
    dist.mkdir(parents=True)
    (dist / "index.html").write_text("<!doctype html><html>spa</html>", encoding="utf-8")
    assets = dist / "assets"
    assets.mkdir()
    (assets / "app.js").write_text("console.log(1)", encoding="utf-8")
    # secret hors de dist (cible d'un path traversal)
    (tmp_path / "secret.txt").write_text("nope", encoding="utf-8")
    monkeypatch.setattr(static_files, "dist_dir", lambda: dist)
    return dist


def test_serves_real_file_with_mime(tmp_path, monkeypatch):
    _build_fake_dist(tmp_path, monkeypatch)
    body, ctype = static_files.resolve("/assets/app.js")
    assert b"console.log" in body
    assert "javascript" in ctype


def test_catch_all_serves_index_html(tmp_path, monkeypatch):
    _build_fake_dist(tmp_path, monkeypatch)
    # chemin inconnu (deep-link SPA) -> index.html
    body, ctype = static_files.resolve("/shortcuts")
    assert b"spa" in body
    assert ctype.startswith("text/html")


def test_root_serves_index(tmp_path, monkeypatch):
    _build_fake_dist(tmp_path, monkeypatch)
    body, _ = static_files.resolve("/")
    assert b"spa" in body


def test_path_traversal_falls_back_to_index(tmp_path, monkeypatch):
    _build_fake_dist(tmp_path, monkeypatch)
    # ../secret.txt ne doit jamais être servi -> retombe sur index.html
    body, ctype = static_files.resolve("/../secret.txt")
    assert b"nope" not in body
    assert ctype.startswith("text/html")


def test_returns_none_when_not_built(monkeypatch):
    monkeypatch.setattr(static_files, "dist_dir", lambda: None)
    assert static_files.resolve("/") is None


def test_module_reimport_is_clean():
    # garde-fou : le module se réimporte sans effet de bord.
    importlib.reload(static_files)
