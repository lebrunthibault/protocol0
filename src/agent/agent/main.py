"""Point d'entrée de l'agent (`poetry run agent`).

Charge la config, démarre l'écoute clavier, sert la page web (launcher), et tourne
jusqu'à interruption. Tourne sous Python système (pynput/ctypes dispo), hors d'Ableton.
"""
import logging
import os
import sys
import time
from logging.handlers import RotatingFileHandler

from agent import key_emitter, single_instance, web
from agent.config import Binding, ShortcutConfig, config_path
from agent.listener import ShortcutListener
from agent.script_client import ScriptClient
from agent.settings import Settings
from agent.version import __version__


def _log_dir() -> str:
    d = os.path.join(os.environ["APPDATA"], "Protocol0", "logs")
    os.makedirs(d, exist_ok=True)
    return d


def _configure_logging() -> None:
    """Logge vers fichier rotatif (%APPDATA%\\Protocol0\\logs\\agent.log) ET console.

    Le fichier est l'unique diagnostic quand l'agent tourne en tâche planifiée
    sans console (exe no-console). Le handler console reste utile en dev terminal et
    devient un no-op silencieux sous l'exe gelé sans console attachée.
    """
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    file_handler = RotatingFileHandler(
        os.path.join(_log_dir(), "agent.log"),
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
    logger = logging.getLogger("agent")
    logger.info("agent version: %s", __version__)

    if sys.platform != "win32":
        logger.error("agent is Windows-only (foreground check is Win32)")
        return

    # Un seul agent à la fois : deux instances = deux hooks clavier = raccourci en double.
    if not single_instance.acquire():
        logger.info("another agent instance is already running, exiting")
        return

    settings = Settings()
    client = ScriptClient(settings)
    config = ShortcutConfig()

    logger.info("config: %s", config_path())
    logger.info("script url override: %s", settings.override_url or "(dynamic via runtime.json)")

    def dispatch(binding: Binding, held_modifiers) -> None:
        # Two action families: `send_keys` is replayed locally (native Live shortcut,
        # no HTTP), everything else goes through the script's HTTP API unchanged.
        # `held_modifiers` is the snapshot the listener took at decision time.
        if binding.action == "send_keys":
            keys = binding.params.get("keys")
            if not keys:
                logger.warning("send_keys binding without 'keys' param")
                return
            # Lift the user's currently-held modifiers so the target chord lands clean
            # (e.g. holding ctrl+alt and tapping the trigger key still sends ctrl+n). The
            # trigger's main key is suppressed by the listener hook, so it can't leak.
            key_emitter.send(keys, held_modifiers=held_modifiers)
        else:
            client.execute(binding)

    listener = ShortcutListener(config, dispatch)
    listener.start()
    # Serveur web (SPA + /api + /status) sur son propre thread daemon :
    # ne bloque ni la boucle ci-dessous ni le listener pynput.
    web.start()
    # Interruptible wait on the main thread: joining the pynput listener thread
    # directly swallows Ctrl+C on Windows, so poll a short sleep instead.
    try:
        while True:
            time.sleep(0.2)
    except KeyboardInterrupt:
        logger.info("stopping")
    finally:
        web.stop()
        listener.stop()


if __name__ == "__main__":
    start()
