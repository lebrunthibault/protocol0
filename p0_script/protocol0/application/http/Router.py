"""Mini routeur HTTP stdlib pour le serveur exposé par le script.

Décorateur @route + un BaseHTTPRequestHandler qui parse l'URL et dispatche.
Reproduit le pattern FastAPI du backend (p0_backend/.../http_server/routes/)
mais sans framework — on n'a accès qu'à la stdlib dans Ableton.
"""
import inspect
from http.server import BaseHTTPRequestHandler
from typing import Callable, Dict, Tuple
from urllib.parse import urlparse, parse_qs

from protocol0.shared.logging.Logger import Logger

# (method, path) -> fonction. Rempli par @route au moment de l'import des
# modules dans routes/__init__.py.
_ROUTES: Dict[Tuple[str, str], Callable] = {}


def route(method: str, path: str) -> Callable:
    def wrap(fn: Callable) -> Callable:
        _ROUTES[(method.upper(), path)] = fn
        return fn

    return wrap


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

        # Pont vers le thread Live : on ne touche surtout pas à l'API Ableton ici
        # (on est sur un thread daemon du serveur HTTP).
        HttpServer.submit(lambda: fn(**kwargs))
        Logger.info("HTTP %s %s" % (method, self.path))

        self.send_response(200)
        self.end_headers()
