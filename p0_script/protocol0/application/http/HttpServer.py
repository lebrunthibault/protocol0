"""HTTP server exposé par le script à 127.0.0.1:9000.

Le serveur tourne sur un thread daemon, mais l'API Live n'est touchable que
depuis le thread main d'Ableton (celui qui pilote Live.Base.Timer). Pour
franchir cette frontière sans risquer de corrompre TickScheduler._scheduled_events
(pas de lock interne), on passe par une queue.Queue (thread-safe par construction)
drainée à chaque tick.
"""
import queue
import threading
from http.server import ThreadingHTTPServer
from queue import Empty
from typing import Callable, Optional

from protocol0.application.ContainerInterface import ContainerInterface
from protocol0.application.http.Router import HttpRequestHandler
from protocol0.domain.shared.errors.error_handler import handle_errors
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.shared.logging.Logger import Logger

# Borne le nombre de callbacks exécutés par tick (~17 ms). Au-delà, on rend
# la main au thread Live pour ne pas allonger le tick en cas de burst de
# requêtes (ex. AHK qui répète une hotkey). Les callbacks restants seront
# traités au tick suivant.
_MAX_CALLBACKS_PER_TICK = 8

_PORT = 9000

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
    _server = ThreadingHTTPServer(("127.0.0.1", _PORT), HttpRequestHandler)
    _thread = threading.Thread(target=_server.serve_forever, daemon=True)
    _thread.start()
    Logger.info("HttpServer listening on 127.0.0.1:%d" % _PORT)


def stop() -> None:
    """Appelé depuis Protocol0.disconnect(). Évite le 'Address already in use'
    lors d'un reload rapide du script — daemon=True ne suffit pas car
    serve_forever() tient le socket."""
    global _server
    if _server is not None:
        _server.shutdown()
        _server.server_close()
        _server = None
