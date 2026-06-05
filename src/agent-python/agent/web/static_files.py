"""Résolution + service du build statique de la SPA (src/frontend/dist).

Le build Vite est embarqué dans l'exe via PyInstaller (datas -> dossier "frontend",
cf. protocol0-agent.spec) et lu via sys._MEIPASS — même idiome que agent/version.py.
En dev (poetry run), on lit src/frontend/dist sur le disque.

Catch-all SPA : tout chemin qui ne correspond pas à un fichier réel sert index.html,
pour que le routing côté client (history mode) fonctionne au refresh / deep-link.
"""
import mimetypes
import sys
from pathlib import Path
from typing import Optional, Tuple


def _frozen_root() -> Optional[Path]:
    base = getattr(sys, "_MEIPASS", None)
    if base:
        d = Path(base) / "frontend"
        if d.is_dir():
            return d
    return None


def _source_root() -> Optional[Path]:
    # Remonte depuis ce fichier jusqu'à la racine du repo, puis src/frontend/dist.
    for parent in Path(__file__).resolve().parents:
        d = parent / "src" / "frontend" / "dist"
        if d.is_dir():
            return d
    return None


def dist_dir() -> Optional[Path]:
    """Racine du build de la SPA (gelé ou source), ou None si pas buildé."""
    return _frozen_root() or _source_root()


def _safe_join(root: Path, url_path: str) -> Optional[Path]:
    # Empêche le path traversal : le chemin résolu doit rester sous root.
    rel = url_path.lstrip("/")
    candidate = (root / rel).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return None
    return candidate


def resolve(url_path: str) -> Optional[Tuple[bytes, str]]:
    """(corps, content-type) pour une requête GET.

    - fichier réel sous dist/ -> ce fichier ;
    - sinon -> index.html (catch-all SPA) ;
    - None si la SPA n'est pas buildée (dist absent ou index.html manquant).
    """
    root = dist_dir()
    if root is None:
        return None

    target = _safe_join(root, url_path)
    if target is not None and target.is_file():
        return target.read_bytes(), _content_type(target)

    index = root / "index.html"
    if index.is_file():
        return index.read_bytes(), "text/html; charset=utf-8"
    return None


def _content_type(path: Path) -> str:
    ctype, _ = mimetypes.guess_type(str(path))
    if ctype is None:
        return "application/octet-stream"
    if ctype.startswith("text/") or ctype in ("application/javascript", "application/json"):
        return ctype + "; charset=utf-8"
    return ctype
