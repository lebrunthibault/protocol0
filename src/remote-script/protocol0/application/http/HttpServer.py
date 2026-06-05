"""HTTP server exposé par le script à 127.0.0.1:9000.

Le serveur tourne sur un thread daemon, mais l'API Live n'est touchable que
depuis le thread main d'Ableton (celui qui pilote Live.Base.Timer). Pour
franchir cette frontière sans risquer de corrompre TickScheduler._scheduled_events
(pas de lock interne), on passe par une queue.Queue (thread-safe par construction)
drainée à chaque tick.
"""
import os
import queue
import threading
from http.server import ThreadingHTTPServer
from queue import Empty
from typing import Callable, Optional

from protocol0.application.ContainerInterface import ContainerInterface
from protocol0.application.http import runtime_state
from protocol0.application.http.Router import HttpRequestHandler
from protocol0.domain.shared.errors.error_handler import handle_errors
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.shared.logging.Logger import Logger
from protocol0.version import __version__

# Borne le nombre de callbacks exécutés par tick (~17 ms). Au-delà, on rend
# la main au thread Live pour ne pas allonger le tick en cas de burst de
# requêtes (ex. AHK qui répète une hotkey). Les callbacks restants seront
# traités au tick suivant.
_MAX_CALLBACKS_PER_TICK = 8

# Port préféré. S'il est déjà pris (autre instance, ou un service squattant 9000),
# on retombe sur un port libre choisi par l'OS (bind sur 0) plutôt que de crasher le
# chargement du script. Le port effectif est publié dans runtime.json pour que
# l'agent le retrouve (best-practice OSS : port fixe + fallback + fichier
# d'adresse, cf. Jupyter/RFC 8252). Override manuel encore possible côté agent via
# P0_SCRIPT_PORT (escape hatch).
_DEFAULT_PORT = 9000

_queue: "queue.Queue[Callable]" = queue.Queue()
_container: Optional[ContainerInterface] = None
_server: Optional[ThreadingHTTPServer] = None
_thread: Optional[threading.Thread] = None


def submit(callback: Callable) -> None:
    """Appelé depuis le thread HTTP. Le callback sera exécuté sur le thread Live."""
    _queue.put(callback)


def get_container() -> ContainerInterface:
    return _container


@handle_errors()
def _drain() -> None:
    """Exécuté sur le thread Live à chaque tick. Vide la queue (cap _MAX_…)
    puis se ré-arme via Scheduler.wait(1, _drain) pour le tick suivant.
    Pas de boucle infinie ici : on rend la main et on revient au prochain tick."""
    for _ in range(_MAX_CALLBACKS_PER_TICK):
        try:
            callback = _queue.get_nowait()
        except Empty:
            break
        # handle_errors sur _drain protège l'itération ; une exception qui
        # remonte ici interromprait le drain pour ce tick mais pas son
        # ré-armement (la ligne Scheduler.wait ci-dessous serait skippée,
        # donc on attrape par sécurité au cas par cas).
        try:
            callback()
        except Exception as e:
            Logger.warning("HTTP callback error: %s" % e)
    Scheduler.wait(1, _drain)


def start(container: ContainerInterface) -> None:
    """Appelé depuis Protocol0._initialize() — donc sur le thread Live."""
    global _container, _server, _thread

    # Import tardif des routes : c'est ici qu'on déclenche l'enregistrement
    # via les décorateurs @route. Faire ça plus tôt (top-level) créerait
    # une dépendance circulaire avec HttpServer.get_container.
    import protocol0.application.http.routes  # noqa: F401

    _container = container

    # Amorce le drain. Sûr car on est déjà sur le thread Live ici.
    Scheduler.wait(1, _drain)

    # ThreadingHTTPServer pour ne pas bloquer entre requêtes concurrentes
    # (AHK peut spammer). Chaque requête est de toute façon fire-and-forget
    # côté thread Live via submit().
    try:
        _server = ThreadingHTTPServer(("127.0.0.1", _DEFAULT_PORT), HttpRequestHandler)
    except OSError:
        # Port préféré pris : laisser l'OS en choisir un libre (bind sur 0).
        _server = ThreadingHTTPServer(("127.0.0.1", 0), HttpRequestHandler)
    port = _server.server_address[1]
    _thread = threading.Thread(target=_server.serve_forever, daemon=True)
    _thread.start()
    Logger.info("HttpServer listening on 127.0.0.1:%d" % port)

    # Publie l'URL effective pour l'agent. os.getpid() ici = PID
    # d'Ableton (le script tourne dans son interpréteur) -> sert au cross-check
    # de fraîcheur côté launcher.
    runtime_state.write("http://127.0.0.1:%d" % port, os.getpid(), __version__)


def stop() -> None:
    """Appelé depuis Protocol0.disconnect(). Évite le 'Address already in use'
    lors d'un reload rapide du script — daemon=True ne suffit pas car
    serve_forever() tient le socket."""
    global _server
    if _server is not None:
        _server.shutdown()
        _server.server_close()
        _server = None
    # Le serveur n'écoute plus : retire le fichier d'état (absence = script inactif
    # pour l'agent).
    runtime_state.clear()
