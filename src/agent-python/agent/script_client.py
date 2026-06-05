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

from agent import action_catalog, runtime_state
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
        """Dispatch générique : on résout l'action dans le catalogue exposé par le script
        (son /openapi.json) au moment du déclenchement, puis on POST sur sa route. Aucune
        action n'est codée en dur — déposer un plugin @action suffit à la rendre exécutable.
        (`send_keys` n'arrive pas ici : il est injecté localement en amont, cf. main.py.)"""
        base_url = self._resolve_base_url()
        if base_url is None:
            logger.info("script not running, ignoring %s" % binding.combo)
            return

        action = next(
            (a for a in action_catalog.fetch(base_url, self._session)
             if a["name"] == binding.action),
            None,
        )
        if action is None:
            logger.warning("unknown action: %s" % binding.action)
            return

        # Body = les params déclarés par l'action, pris dans le binding (manquant -> omis ;
        # le script renvoie 400 si un required manque, ce que _post logge).
        body = {
            p["name"]: binding.params[p["name"]]
            for p in action["params"]
            if p["name"] in binding.params
        }
        # Mutation -> POST sous /api (API REST : GET en lecture, POST en mutation), args en
        # body JSON. La route /action/<plugin>/<method> est générée par le plugin via @action.
        self._post(base_url, "/api" + action["path"], body)

    def _post(self, base_url: str, path: str, body: dict) -> None:
        url = base_url + path
        try:
            r = self._session.post(url, json=body, timeout=5)
            r.raise_for_status()
        except requests.RequestException as e:
            logger.warning("script HTTP %s failed: %s" % (path, e))
