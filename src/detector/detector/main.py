"""Point d'entrée du détecteur (`poetry run detector`).

Charge la config, démarre l'écoute clavier, et tourne jusqu'à interruption.
Tourne sous Python système (pynput/ctypes dispo), hors d'Ableton.
"""
import logging
import sys
import time

from detector.config import ShortcutConfig, config_path
from detector.listener import ShortcutListener
from detector.script_client import ScriptClient
from detector.settings import Settings


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def start() -> None:
    _configure_logging()
    logger = logging.getLogger("detector")

    if sys.platform != "win32":
        logger.error("detector prototype is Windows-only (foreground check is Win32)")
        return

    settings = Settings()
    client = ScriptClient(settings.p0_script_url)
    config = ShortcutConfig()

    logger.info("config: %s", config_path())
    logger.info("script: %s", settings.p0_script_url)

    listener = ShortcutListener(config, client.execute)
    listener.start()
    # Interruptible wait on the main thread: joining the pynput listener thread
    # directly swallows Ctrl+C on Windows, so poll a short sleep instead.
    try:
        while True:
            time.sleep(0.2)
    except KeyboardInterrupt:
        logger.info("stopping")
    finally:
        listener.stop()


if __name__ == "__main__":
    start()
