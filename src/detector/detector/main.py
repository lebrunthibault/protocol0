"""Point d'entrée du détecteur (`poetry run detector`).

Charge la config, démarre l'écoute clavier, et tourne jusqu'à interruption.
Tourne sous Python système (pynput/ctypes dispo), hors d'Ableton.
"""
import logging
import os
import sys
import time
from logging.handlers import RotatingFileHandler

from detector import launcher, single_instance
from detector.config import ShortcutConfig, config_path
from detector.listener import ShortcutListener
from detector.script_client import ScriptClient
from detector.settings import Settings
from detector.version import __version__


def _log_dir() -> str:
    d = os.path.join(os.environ["APPDATA"], "Protocol0", "logs")
    os.makedirs(d, exist_ok=True)
    return d


def _configure_logging() -> None:
    """Logge vers fichier rotatif (%APPDATA%\\Protocol0\\logs\\detector.log) ET console.

    Le fichier est l'unique diagnostic quand le détecteur tourne en tâche planifiée
    sans console (exe no-console). Le handler console reste utile en dev terminal et
    devient un no-op silencieux sous l'exe gelé sans console attachée.
    """
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    file_handler = RotatingFileHandler(
        os.path.join(_log_dir(), "detector.log"),
        maxBytes=2_000_000,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(fmt)
    root.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(fmt)
    root.addHandler(console_handler)


def start() -> None:
    _configure_logging()
    logger = logging.getLogger("detector")
    logger.info("detector version: %s", __version__)

    if sys.platform != "win32":
        logger.error("detector prototype is Windows-only (foreground check is Win32)")
        return

    # Un seul detector à la fois : deux instances = deux hooks clavier = raccourci en double.
    if not single_instance.acquire():
        logger.info("another detector instance is already running, exiting")
        return

    settings = Settings()
    client = ScriptClient(settings)
    config = ShortcutConfig()

    logger.info("config: %s", config_path())
    logger.info("script url override: %s", settings.override_url or "(dynamic via runtime.json)")

    listener = ShortcutListener(config, client.execute)
    listener.start()
    # Launcher web (diagnostic + redirection vers l'UI) sur son propre thread daemon :
    # ne bloque ni la boucle ci-dessous ni le listener pynput.
    launcher.start()
    # Interruptible wait on the main thread: joining the pynput listener thread
    # directly swallows Ctrl+C on Windows, so poll a short sleep instead.
    try:
        while True:
            time.sleep(0.2)
    except KeyboardInterrupt:
        logger.info("stopping")
    finally:
        launcher.stop()
        listener.stop()


if __name__ == "__main__":
    start()
