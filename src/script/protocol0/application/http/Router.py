"""Mini routeur HTTP stdlib pour le serveur exposé par le script.

Décorateur @route + un BaseHTTPRequestHandler qui parse l'URL et dispatche.
Reproduit le pattern FastAPI (décorateur de route + dispatch) mais sans
framework — on n'a accès qu'à la stdlib dans Ableton.
"""
import inspect
import json
import threading
from http.server import BaseHTTPRequestHandler
from typing import Callable, Dict, Tuple
from urllib.parse import urlparse, parse_qs

from protocol0.shared.logging.Logger import Logger

# (method, path) -> fonction. Rempli par @route au moment de l'import des
# modules dans routes/__init__.py.
_ROUTES: Dict[Tuple[str, str], Callable] = {}

# Borne d'attente du thread HTTP pendant que le handler s'exécute sur le
# thread Live. L'API Live répond en quelques ms à un tick (~17 ms) ; 2 s laisse
# largement la marge même sous burst.
_HANDLER_TIMEOUT_S = 2.0


def route(method: str, path: str) -> Callable:
    def wrap(fn: Callable) -> Callable:
        _ROUTES[(method.upper(), path)] = fn
        return fn

    return wrap


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


def _build_kwargs(fn: Callable, query: Dict[str, list]) -> dict:
    sig = inspect.signature(fn)
    kwargs = {}
    for name, param in sig.parameters.items():
        if name not in query:
            if param.default is inspect.Parameter.empty:
                raise ValueError("missing query param: %s" % name)
            continue
        kwargs[name] = _coerce(query[name][0], param.annotation)
    return kwargs


def _returns_value(fn: Callable) -> bool:
    """Vrai si le handler a une annotation de retour non-None (donc on attend
    son résultat pour le sérialiser en JSON). Sinon fire-and-forget."""
    ann = inspect.signature(fn).return_annotation
    return ann is not inspect.Signature.empty and ann is not None and ann is not type(None)


class HttpRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802 (imposé par BaseHTTPRequestHandler)
        self._dispatch("GET")

    def log_message(self, format: str, *args) -> None:
        # Évite d'inonder stderr avec les access logs stdlib ; on log via
        # notre Logger uniquement en cas de succès/erreur de dispatch.
        pass

    def _dispatch(self, method: str) -> None:
        # Import tardif pour éviter une dépendance circulaire HttpServer<->Router
        from protocol0.application.http import HttpServer

        parsed = urlparse(self.path)
        fn = _ROUTES.get((method, parsed.path))
        if fn is None:
            self.send_response(404)
            self.end_headers()
            return

        try:
            kwargs = _build_kwargs(fn, parse_qs(parsed.query))
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

        result = slot["result"]
        if isinstance(result, str):
            body = result.encode("utf-8")
            content_type = "text/html; charset=utf-8"
        else:
            body = json.dumps(result).encode("utf-8")
            content_type = "application/json"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
