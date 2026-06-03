"""Serveur web de l'agent (port fixe 9010, thread daemon).

Sert, dans l'ordre de dispatch :
  1. les routes API (/api/* et /status) via agent.web.api ;
  2. sinon, le build statique de la SPA (catch-all -> index.html) via agent.web.static_files.

Lifecycle (bind 9010 + retry en arrière-plan si pris) porté de l'ancien launcher.py : si
9010 est occupé, on log et on réessaie — PAS de fallback aléatoire (le raccourci .url est
câblé sur 9010). Le clavier continue de fonctionner même si le serveur ne bind jamais.
"""
import logging
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from agent.settings import WEB_PORT
from agent.web import api, static_files

logger = logging.getLogger("agent")

_RETRY_INTERVAL_S = 30.0

_server = None  # type: ThreadingHTTPServer | None
_thread = None  # type: threading.Thread | None
_retry_thread = None  # type: threading.Thread | None
_stop = threading.Event()


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802 (imposé par BaseHTTPRequestHandler)
        self._dispatch("GET", b"")

    def do_POST(self) -> None:  # noqa: N802
        length = int(self.headers.get("Content-Length", 0) or 0)
        body = self.rfile.read(length) if length else b""
        self._dispatch("POST", body)

    def log_message(self, format: str, *args) -> None:
        # Pas d'access log sur stderr.
        pass

    def _dispatch(self, method: str, body: bytes) -> None:
        parsed = urlparse(self.path)
        # 1) routes API + /status.
        resp = api.handle(method, parsed.path, parsed.query, body)
        if resp is not None:
            code, payload, ctype = resp
            self._send(code, payload, ctype)
            return
        # 2) fichiers statiques de la SPA (GET seulement).
        if method == "GET":
            served = static_files.resolve(parsed.path)
            if served is not None:
                payload, ctype = served
                self._send(200, payload, ctype)
                return
            # SPA non buildée : message explicite plutôt qu'un 404 muet.
            self._send(
                500,
                b"frontend not built - run: cd src/frontend && npm ci && npm run build",
                "text/plain; charset=utf-8",
            )
            return
        self._send(404, b"not found", "text/plain; charset=utf-8")

    def _send(self, code: int, body: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def _try_bind() -> bool:
    """Tente de binder 9010. True si le serveur tourne, False si le port est pris."""
    global _server, _thread
    try:
        _server = ThreadingHTTPServer(("127.0.0.1", WEB_PORT), _Handler)
    except OSError as e:
        logger.warning("web server could not bind 127.0.0.1:%d (%s)" % (WEB_PORT, e))
        return False
    _thread = threading.Thread(target=_server.serve_forever, daemon=True)
    _thread.start()
    logger.info("web server listening on http://127.0.0.1:%d" % WEB_PORT)
    return True


def _retry_loop() -> None:
    while not _stop.wait(_RETRY_INTERVAL_S):
        if _try_bind():
            return


def start() -> None:
    """Démarre le serveur web. Si 9010 est pris, réessaie en arrière-plan jusqu'à stop()."""
    global _retry_thread
    _stop.clear()
    if _try_bind():
        return
    _retry_thread = threading.Thread(target=_retry_loop, daemon=True)
    _retry_thread.start()


def stop() -> None:
    global _server
    _stop.set()
    if _server is not None:
        _server.shutdown()
        _server.server_close()
        _server = None
