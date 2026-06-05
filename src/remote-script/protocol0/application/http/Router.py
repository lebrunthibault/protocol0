"""Mini routeur HTTP stdlib pour le serveur exposé par le script.

Décorateurs @route / @api_route + un BaseHTTPRequestHandler qui parse l'URL et
dispatche. Reproduit le pattern FastAPI (décorateur de route + dispatch) mais sans
framework — on n'a accès qu'à la stdlib dans Ableton.

Surface :
  - @api_route(method, "/device/load")  -> enregistre "/api/device/load" (les
    actions vivent sous /api ; c'est une vraie API REST JSON).
  - @route(method, "/docs")             -> enregistre le chemin tel quel (pour les
    routes hors-API : "/", "/docs", "/openapi.json").

Mutations en POST, lectures en GET (cf. spec
docs/specs/.../2026-06-04-script-rest-api-and-swagger.md). Le body POST est lu en
JSON ; les query params restent supportés pour les GET.
"""
import inspect
import json
import threading
from http.server import BaseHTTPRequestHandler
from typing import Callable, Dict, Tuple
from urllib.parse import urlparse, parse_qs

from protocol0.shared.logging.Logger import Logger

# Préfixe de toutes les routes d'action. Centralisé ici pour que @api_route et le
# générateur OpenAPI partagent la même source de vérité.
API_PREFIX = "/api"

# (method, path) -> fonction. Rempli par @route/@api_route au moment de l'import
# des modules dans routes/__init__.py.
_ROUTES: Dict[Tuple[str, str], Callable] = {}

# Borne d'attente du thread HTTP pendant que le handler s'exécute sur le
# thread Live. L'API Live répond en quelques ms à un tick (~17 ms) ; 2 s laisse
# largement la marge même sous burst.
_HANDLER_TIMEOUT_S = 2.0


def route(method: str, path: str) -> Callable:
    """Enregistre une route au chemin EXACT (pas de préfixe). Pour les routes
    hors-API : "/", "/docs", "/openapi.json"."""

    def wrap(fn: Callable) -> Callable:
        _ROUTES[(method.upper(), path)] = fn
        return fn

    return wrap


def api_route(method: str, path: str) -> Callable:
    """Enregistre une route d'action sous API_PREFIX. ``@api_route("POST",
    "/device/load")`` -> "/api/device/load". Les plugins l'utilisent aussi pour
    que leurs actions vivent sous /api et apparaissent dans /openapi.json."""
    return route(method, API_PREFIX + path)


def get_routes() -> Dict[Tuple[str, str], Callable]:
    return _ROUTES


def _coerce(value: str, annotation: type):
    # Mini coerce pour les types primitifs supportés par les query params
    # (calque grossier de ce que FastAPI fait depuis les annotations).
    if annotation is int:
        return int(value)
    if annotation is bool:
        return value.lower() in ("1", "true", "yes")
    return value  # str ou pas d'annotation


def _build_kwargs(fn: Callable, source: Dict[str, object]) -> dict:
    """Construit les kwargs depuis une source plate {nom: valeur}. ``source`` vient
    des query params (GET) ou du body JSON (POST). On coerce uniquement les valeurs
    str (query) ; un body JSON arrive déjà typé."""
    sig = inspect.signature(fn)
    kwargs = {}
    for name, param in sig.parameters.items():
        if name not in source:
            if param.default is inspect.Parameter.empty:
                raise ValueError("missing param: %s" % name)
            continue
        value = source[name]
        kwargs[name] = _coerce(value, param.annotation) if isinstance(value, str) else value
    return kwargs


def _returns_value(fn: Callable) -> bool:
    """Vrai si le handler a une annotation de retour non-None (donc on attend
    son résultat pour le sérialiser en JSON). Sinon fire-and-forget."""
    ann = inspect.signature(fn).return_annotation
    return ann is not inspect.Signature.empty and ann is not None and ann is not type(None)


class HttpRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802 (imposé par BaseHTTPRequestHandler)
        self._dispatch("GET", {})

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", 0) or 0)
        raw = self.rfile.read(length) if length else b""
        try:
            body = json.loads(raw) if raw else {}
            if not isinstance(body, dict):
                body = {}
        except ValueError:
            body = {}
        self._dispatch("POST", body)

    def log_message(self, format: str, *args) -> None:
        # Évite d'inonder stderr avec les access logs stdlib ; on log via
        # notre Logger uniquement en cas de succès/erreur de dispatch.
        pass

    def _dispatch(self, method: str, body: Dict[str, object]) -> None:
        # Import tardif pour éviter une dépendance circulaire HttpServer<->Router
        from protocol0.application.http import HttpServer

        parsed = urlparse(self.path)

        # Assets statiques de la Swagger UI (/docs/<asset>) : servis directement,
        # sans passer par le pont thread Live (lecture de fichier pure-Python).
        # /docs lui-même est une route enregistrée (voir index_routes).
        if method == "GET" and parsed.path.startswith("/docs/"):
            from protocol0.application.http import swagger_ui

            served = swagger_ui.resolve(parsed.path)
            if served is not None:
                body, content_type = served
                self._write_result(Response.bytes(body, content_type))
            else:
                self.send_response(404)
                self.end_headers()
            return

        fn = _ROUTES.get((method, parsed.path))
        if fn is None:
            self.send_response(404)
            self.end_headers()
            return

        # GET -> query params ; POST -> body JSON (déjà parsé). On aplatit les
        # query (parse_qs renvoie des listes) pour matcher la forme du body.
        if method == "GET":
            source: Dict[str, object] = {k: v[0] for k, v in parse_qs(parsed.query).items()}
        else:
            source = dict(body)

        try:
            kwargs = _build_kwargs(fn, source)
        except ValueError as e:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(str(e).encode())
            return

        Logger.info("HTTP %s %s" % (method, self.path))

        if not _returns_value(fn):
            # Pont vers le thread Live : on ne touche surtout pas à l'API Ableton ici
            # (on est sur un thread daemon du serveur HTTP).
            HttpServer.submit(lambda: fn(**kwargs))
            self.send_response(200)
            self.end_headers()
            return

        # Handler avec retour : on attend le résultat depuis le thread Live.
        done = threading.Event()
        slot: dict = {}

        def run() -> None:
            try:
                slot["result"] = fn(**kwargs)
            except Exception as e:
                slot["error"] = e
            finally:
                done.set()

        HttpServer.submit(run)

        if not done.wait(_HANDLER_TIMEOUT_S):
            self.send_response(504)
            self.end_headers()
            self.wfile.write(b"handler timeout")
            return

        if "error" in slot:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(slot["error"]).encode())
            return

        self._write_result(slot["result"])

    def _write_result(self, result) -> None:
        """Sérialise le retour d'un handler. Un Response (code/body/content-type
        explicite) court-circuite la sérialisation par défaut — c'est ainsi que /,
        /docs et /openapi.json contrôlent leur réponse (redirect, HTML, JSON brut)."""
        if isinstance(result, Response):
            self.send_response(result.status)
            for key, value in result.headers.items():
                self.send_header(key, value)
            self.send_header("Content-Length", str(len(result.body)))
            self.end_headers()
            if result.body:
                self.wfile.write(result.body)
            return

        if isinstance(result, str):
            body = result.encode("utf-8")
            content_type = "text/html; charset=utf-8"
        else:
            body = json.dumps(result).encode("utf-8")
            content_type = "application/json; charset=utf-8"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class Response(object):
    """Réponse HTTP explicite renvoyée par un handler qui veut contrôler le code,
    les headers et le corps (redirect, HTML, JSON brut, asset statique). Les
    handlers d'action courants n'en ont pas besoin : renvoyer un dict/str suffit."""

    def __init__(self, status: int, body: bytes = b"", headers: Dict[str, str] = None) -> None:
        self.status = status
        self.body = body
        self.headers = headers or {}

    @classmethod
    def redirect(cls, location: str, status: int = 302) -> "Response":
        return cls(status, b"", {"Location": location})

    @classmethod
    def json(cls, payload, status: int = 200) -> "Response":
        body = json.dumps(payload).encode("utf-8")
        return cls(status, body, {"Content-Type": "application/json; charset=utf-8"})

    @classmethod
    def bytes(cls, body: bytes, content_type: str, status: int = 200) -> "Response":
        return cls(status, body, {"Content-Type": content_type})
