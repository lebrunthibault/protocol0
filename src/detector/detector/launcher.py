"""Serveur "launcher" servi par le detector (toujours vivant via la tâche planifiée).

Le serveur HTTP de config (page /shortcuts) est servi par le script DANS Ableton : il
meurt avec Ableton. Le launcher, lui, survit et porte donc le diagnostic quand le script
est injoignable. Le raccourci Windows (.url) pointe sur http://127.0.0.1:9010/.

La page interroge GET /status et affiche l'un de trois états :
  - no_ableton      : Ableton pas lancé.
  - script_inactive : Ableton lancé mais control surface pas activée (ou figée).
  - ready           : script joignable -> redirige vers son UI /shortcuts.

Tourne sur un thread daemon (comme le serveur du script) : ne bloque ni la boucle
principale ni le listener pynput. Si le port 9010 est pris, on log et on réessaie en
arrière-plan — PAS de fallback aléatoire (le raccourci est câblé sur 9010). Le clavier
continue de fonctionner même si le launcher ne bind jamais.
"""
import json
import logging
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import requests

from detector import process_check, runtime_state
from detector.settings import LAUNCHER_PORT

logger = logging.getLogger("detector")

HELP_URL = "https://www.protocol0.live/"

_RETRY_INTERVAL_S = 30.0

_server = None  # type: ThreadingHTTPServer | None
_thread = None  # type: threading.Thread | None
_retry_thread = None  # type: threading.Thread | None
_stop = threading.Event()


def _status() -> dict:
    """Calcule l'état courant (no_ableton / script_inactive / ready)."""
    if not process_check.ableton_is_running():
        return {"state": "no_ableton"}
    rt = runtime_state.read()
    if rt and _ping(rt["script_url"]):
        return {"state": "ready", "script_url": rt["script_url"]}
    return {"state": "script_inactive"}


def _ping(script_url: str) -> bool:
    try:
        r = requests.get(script_url + "/health", timeout=1)
        return r.status_code == 200
    except requests.RequestException:
        return False


class _LauncherHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802 (imposé par BaseHTTPRequestHandler)
        if self.path == "/status":
            self._send_json(_status())
        elif self.path == "/" or self.path.startswith("/?"):
            self._send_html(_PAGE)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format: str, *args) -> None:
        # Pas d'access log sur stderr.
        pass

    def _send_json(self, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, page: str) -> None:
        body = page.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def _try_bind() -> bool:
    """Tente de binder 9010. True si le serveur tourne, False si le port est pris."""
    global _server, _thread
    try:
        _server = ThreadingHTTPServer(("127.0.0.1", LAUNCHER_PORT), _LauncherHandler)
    except OSError as e:
        logger.warning("launcher could not bind 127.0.0.1:%d (%s)" % (LAUNCHER_PORT, e))
        return False
    _thread = threading.Thread(target=_server.serve_forever, daemon=True)
    _thread.start()
    logger.info("launcher listening on http://127.0.0.1:%d" % LAUNCHER_PORT)
    return True


def _retry_loop() -> None:
    while not _stop.wait(_RETRY_INTERVAL_S):
        if _try_bind():
            return


def start() -> None:
    """Démarre le launcher. Si 9010 est pris, réessaie en arrière-plan jusqu'à stop()."""
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


# Page HTML/JS inline (zéro build, fetch vanilla — même philosophie que la page /shortcuts
# du script). Attention : le JS contient des { } littéraux -> ne jamais passer cette string
# dans str.format / %.
_PAGE = (
    """<!doctype html><html><head><meta charset='utf-8'>
<title>Protocol 0</title>
<style>
body{font-family:sans-serif;max-width:560px;margin:4em auto;padding:0 1em;text-align:center}
h1{font-weight:600}
#card{margin-top:2em;padding:1.5em;border:1px solid #ddd;border-radius:8px}
.msg{font-size:1.1em;line-height:1.5}
.muted{color:#888;font-size:.9em;margin-top:1em}
a{color:#4a90d9}
.spin{color:#888}
</style></head><body>
<h1>Protocol 0</h1>
<div id='card'><p class='msg spin'>Checking…</p></div>

<script>
const HELP = '"""
    + HELP_URL
    + """';
let navigated = false;

function render(state, scriptUrl){
  const card = document.getElementById('card');
  if(state === 'ready'){
    if(navigated) return;
    navigated = true;
    card.innerHTML = "<p class='msg'>Opening Protocol&nbsp;0…</p>";
    window.location = scriptUrl + '/shortcuts';
    return;
  }
  let msg;
  if(state === 'no_ableton'){
    msg = "Protocol&nbsp;0 is accessible only when Ableton is running.";
  } else {
    msg = "Please activate the Protocol&nbsp;0 remote script inside Ableton "
        + "(Preferences \\u2192 Link/Tempo/MIDI).";
  }
  card.innerHTML = "<p class='msg'>" + msg + "</p>"
    + "<p class='muted'><a href='" + HELP + "' target='_blank'>Need help?</a></p>";
}

async function poll(){
  if(navigated) return;
  try{
    const r = await fetch('/status');
    const s = await r.json();
    render(s.state, s.script_url);
  }catch(e){ /* launcher momentanément indispo : on retentera */ }
}

poll();
setInterval(poll, 2000);
</script>
</body></html>"""
)
