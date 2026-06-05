"""Icône systray de l'agent (la surface visible « cet outil tourne, voici Quit »).

Pourquoi un tray : l'agent est un process à hook clavier global qui tourne en
arrière-plan — exactement la silhouette d'un keylogger. Une icône visible + un Quit
un-clic transforment la lecture « spyware » → « un outil que je fais tourner ». C'est
de l'UI, pas un comportement : ça ne change pas le profil antivirus (cf. spec
2026-06-05-systray-and-startup-folder-autostart.md).

  - clic-gauche (action par défaut)  -> ouvre la page config dans le navigateur ;
  - clic-droit (menu)                -> ligne de statut (/status) + Open config +
                                        Open releases page + Quit.

Tourne sur son propre thread (pystray run_detached), comme le serveur web : ne bloque
ni la boucle principale de main.py ni le listener pynput. Le Quit appelle le callback
on_quit fourni par main.py (qui arrête proprement web + listener et débloque la boucle).
"""
import logging
import sys
import webbrowser
from pathlib import Path
from typing import Callable, Optional

import pystray
from PIL import Image

from agent.settings import WEB_PORT
from agent.web import status

logger = logging.getLogger("agent")

CONFIG_URL = "http://127.0.0.1:%d/shortcuts" % WEB_PORT
# Page releases : un LIEN ouvert dans le navigateur, jamais un download+exec (garde le
# profil AV propre ; la mise à jour reste un acte manuel, cf. spec).
RELEASES_URL = "https://www.protocol0.live/"

# Libellés des 3 états calculés par status.compute(), pour la ligne de menu non-cliquable.
_STATE_LABELS = {
    "ready": "Connected to Ableton",
    "script_inactive": "Ableton open - activate the remote script",
    "no_ableton": "Ableton not running",
}

_icon = None  # type: Optional[pystray.Icon]


def _icon_path() -> Optional[Path]:
    """Résout protocol0.ico : exe gelé (embarqué via _MEIPASS) ou sources (repo).

    Même logique que agent/version.py pour VERSION. En gelé, le .ico est ajouté aux
    datas du .spec ; en sources, il vit dans installer/assets/ à la racine du repo.
    """
    base = getattr(sys, "_MEIPASS", None)
    if base:
        f = Path(base) / "protocol0.ico"
        if f.exists():
            return f
    for parent in Path(__file__).resolve().parents:
        f = parent / "installer" / "assets" / "protocol0.ico"
        if f.exists():
            return f
    return None


def _load_image() -> Image.Image:
    path = _icon_path()
    if path is not None:
        return Image.open(path)
    # Dernier recours : un carré uni plutôt que de crasher le tray (donc l'agent).
    logger.warning("tray icon protocol0.ico not found; using a fallback square")
    return Image.new("RGBA", (64, 64), (40, 40, 40, 255))


def _open_config(*_args) -> None:
    webbrowser.open(CONFIG_URL, new=2)


def _open_releases(*_args) -> None:
    webbrowser.open(RELEASES_URL, new=2)


def _status_label(*_args) -> str:
    try:
        state = status.compute().get("state")
    except Exception as e:  # le tray ne doit jamais mourir à cause d'un /status qui throw
        logger.debug("tray status check failed: %s" % e)
        state = None
    return _STATE_LABELS.get(state, "Status unavailable")


def _build_menu(on_quit: Callable[[], None]) -> pystray.Menu:
    def quit_action(icon, _item) -> None:
        logger.info("quit requested from tray")
        on_quit()
        icon.stop()

    return pystray.Menu(
        # default=True : le clic-gauche déclenche cet item (ouvre la config).
        pystray.MenuItem("Open config", _open_config, default=True),
        # enabled=False : ligne de statut purement informative. Le label est un callable
        # -> recalculé à chaque ouverture du menu (statut toujours frais).
        pystray.MenuItem(_status_label, None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Open releases page", _open_releases),
        pystray.MenuItem("Quit", quit_action),
    )


def start(on_quit: Callable[[], None]) -> None:
    """Démarre l'icône systray sur son propre thread. on_quit est appelé au clic sur Quit."""
    global _icon
    _icon = pystray.Icon(
        "protocol0",
        icon=_load_image(),
        title="Protocol 0",
        menu=_build_menu(on_quit),
    )
    # run_detached : pystray gère sa boucle de message sur son propre thread, on rend la
    # main à main.py immédiatement.
    _icon.run_detached()
    logger.info("systray icon started")


def stop() -> None:
    """Retire l'icône (appelé depuis l'arrêt propre si le Quit ne vient pas du tray)."""
    global _icon
    if _icon is not None:
        _icon.stop()
        _icon = None
