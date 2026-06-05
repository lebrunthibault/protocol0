"""Sert la Swagger UI vendorée (offline) sous /docs.

Le dist Swagger UI est embarqué dans le package (``swagger_ui/`` à côté de ce
fichier) et copié tel quel à l'installation (stage_remote_script fait un copytree
du package) — donc on résout les assets relativement à ``__file__``, sans _MEIPASS
ni dépendance CDN.

Chemins servis :
  - /docs               -> swagger_ui/index.html
  - /docs/<asset>       -> swagger_ui/<asset>  (css, bundle js)
"""
import mimetypes
from pathlib import Path
from typing import Optional, Tuple

_DIST = Path(__file__).resolve().parent / "swagger_ui"


def _content_type(path: Path) -> str:
    ctype, _ = mimetypes.guess_type(str(path))
    if ctype is None:
        return "application/octet-stream"
    if ctype.startswith("text/") or ctype in ("application/javascript", "application/json"):
        return ctype + "; charset=utf-8"
    return ctype


def resolve(url_path: str) -> Optional[Tuple[bytes, str]]:
    """(corps, content-type) pour un chemin /docs ou /docs/<asset>. None si l'asset
    n'existe pas (le dispatcher renverra alors 404). Anti path-traversal : le chemin
    résolu doit rester sous le dossier dist."""
    if url_path == "/docs" or url_path == "/docs/":
        target = _DIST / "index.html"
    else:
        rel = url_path[len("/docs/"):]  # ex. "swagger-ui.css"
        candidate = (_DIST / rel).resolve()
        try:
            candidate.relative_to(_DIST.resolve())
        except ValueError:
            return None
        target = candidate

    if not target.is_file():
        return None
    return target.read_bytes(), _content_type(target)
