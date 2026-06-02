"""Client HTTP vers l'API du remote script (:9000).

Le détecteur ne fait que remplacer AHK comme producteur d'événements :
l'API d'action exposée par le script est inchangée.
"""
import logging

import requests

from detector.config import Binding

logger = logging.getLogger("detector")


class ScriptClient:
    def __init__(self, base_url: str) -> None:
        self._base_url = base_url
        self._session = requests.Session()

    def execute(self, binding: Binding) -> None:
        """Mappe un binding vers une route du script. Proto : load_device seul."""
        if binding.action == "load_device":
            name = binding.params.get("name")
            if not name:
                logger.warning("load_device binding without 'name' param")
                return
            self._get("/device/load", {"name": name})
        else:
            logger.warning("unknown action: %s" % binding.action)

    def _get(self, path: str, params: dict) -> None:
        url = self._base_url + path
        try:
            r = self._session.get(url, params=params, timeout=5)
            r.raise_for_status()
        except requests.RequestException as e:
            logger.warning("script HTTP %s failed: %s" % (path, e))
