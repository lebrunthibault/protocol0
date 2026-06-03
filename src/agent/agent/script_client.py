"""Client HTTP vers l'API du remote script.

L'agent ne fait que remplacer AHK comme producteur d'événements :
l'API d'action exposée par le script est inchangée.

L'URL de base est résolue À CHAQUE APPEL, pas une fois pour toutes : l'agent vit du
logon au logoff, alors qu'Ableton (et son serveur, sur un port dynamique) démarre/s'arrête
plusieurs fois entre-temps. On lit donc l'URL courante depuis P0_SCRIPT_PORT (override) ou
runtime.json à chaque exécution d'un binding ; absence = script pas actif = no-op.
"""
import logging
from typing import Optional

import requests

from agent import runtime_state
from agent.config import Binding
from agent.settings import Settings

logger = logging.getLogger("agent")


class ScriptClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._session = requests.Session()

    def _resolve_base_url(self) -> Optional[str]:
        # 1) override manuel (P0_SCRIPT_PORT) ; 2) découverte via runtime.json ; 3) None.
        if self._settings.override_url:
            return self._settings.override_url
        rt = runtime_state.read()
        return rt["script_url"] if rt else None

    def execute(self, binding: Binding) -> None:
        """Mappe un binding vers une route du script. Proto : load_device seul."""
        base_url = self._resolve_base_url()
        if base_url is None:
            logger.info("script not running, ignoring %s" % binding.combo)
            return
        if binding.action == "load_device":
            name = binding.params.get("name")
            if not name:
                logger.warning("load_device binding without 'name' param")
                return
            self._get(base_url, "/device/load", {"name": name})
        else:
            logger.warning("unknown action: %s" % binding.action)

    def _get(self, base_url: str, path: str, params: dict) -> None:
        url = base_url + path
        try:
            r = self._session.get(url, params=params, timeout=5)
            r.raise_for_status()
        except requests.RequestException as e:
            logger.warning("script HTTP %s failed: %s" % (path, e))
