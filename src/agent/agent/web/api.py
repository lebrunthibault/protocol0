"""Handlers de l'API web de l'agent (sous /api) + /status.

Renvoient tous (status_code, body_bytes, content_type). Le serveur (server.py) dispatch
les chemins et écrit la réponse. Stdlib only. L'agent écrit shortcuts.json directement
(agent.shortcut_store) ; le listener relit par mtime.

Mutations acceptées en GET (query) ET POST (body JSON) : la SPA utilise POST.
"""
import json
from typing import Dict, Optional, Tuple
from urllib.parse import parse_qs

from agent import ableton_shortcuts, action_catalog, shortcut_store
from agent.version import __version__
from agent.web import status

Response = Tuple[int, bytes, str]
_JSON = "application/json; charset=utf-8"


def _json(payload, code: int = 200) -> Response:
    return code, json.dumps(payload).encode("utf-8"), _JSON


def _error(message: str, code: int = 400) -> Response:
    return _json({"error": message}, code)


def _combo_action_params(data: Dict) -> Tuple[Optional[str], Optional[str], Dict[str, str]]:
    combo = data.get("combo")
    action = data.get("action")
    params = data.get("params") or {}
    if not isinstance(params, dict):
        params = {}
    return combo, action, params


def handle(method: str, path: str, query: str, body: bytes) -> Optional[Response]:
    """Dispatch d'un chemin /api/* ou /status. None si le chemin n'est pas une route API
    (le serveur tentera alors les fichiers statiques)."""
    if path == "/status" and method == "GET":
        return _json(status.compute())

    if path == "/api/health" and method == "GET":
        return _json({"ok": True, "version": __version__})

    if path == "/api/actions" and method == "GET":
        return _json(action_catalog.get_catalog())

    if path == "/api/ableton-shortcuts" and method == "GET":
        # Curated native Live shortcuts the UI offers as remap targets (send_keys).
        return _json(
            {"doc_url": ableton_shortcuts.DOC_URL, "shortcuts": ableton_shortcuts.get_all()}
        )

    if path == "/api/shortcuts" and method == "GET":
        return _json(shortcut_store.list_bindings())

    if path == "/api/shortcuts/add" and method in ("GET", "POST"):
        data = _parse_input(method, query, body)
        combo, action, params = _combo_action_params(data)
        if not combo or not action:
            return _error("combo and action are required")
        return _json(shortcut_store.upsert(combo, action, params))

    if path == "/api/shortcuts/delete" and method in ("GET", "POST"):
        data = _parse_input(method, query, body)
        combo = data.get("combo")
        if not combo:
            return _error("combo is required")
        return _json(shortcut_store.delete(combo))

    # Chemin /api/* inconnu -> 404 JSON (ne pas retomber sur la SPA pour une route API).
    if path.startswith("/api/"):
        return _error("not found", 404)

    return None


def _parse_input(method: str, query: str, body: bytes) -> Dict:
    """Body JSON (POST) ou query params (GET). `params` en GET = blob JSON url-décodé."""
    if method == "POST":
        try:
            data = json.loads(body or b"{}")
        except ValueError:
            return {}
        return data if isinstance(data, dict) else {}
    # GET : query params plats ; params est un blob JSON.
    q = parse_qs(query)
    out: Dict = {}
    for k, v in q.items():
        out[k] = v[0]
    if "params" in out:
        try:
            parsed = json.loads(out["params"])
            out["params"] = parsed if isinstance(parsed, dict) else {}
        except ValueError:
            out["params"] = {}
    return out
