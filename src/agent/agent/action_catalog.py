"""Catalogue statique des actions assignables, servi à la SPA (/api/actions).

Statique (et non plus dérivé des @route du script) pour que le sélecteur d'action du
keymapper fonctionne SANS Ableton. Même forme JSON que l'ex-get_catalog() du script :
    { name, label, params: [{name, type, required}], path, method }

COUPLAGE : garder en phase avec agent.script_client.ScriptClient.execute — une action
listée ici doit être dispatchable là-bas. Le namespace est volontairement petit tant que
l'agent ne sait mapper que load_device ; on l'élargit au fur et à mesure.
"""
from typing import Any, Dict, List

_CATALOG: List[Dict[str, Any]] = [
    {
        "name": "load_device",
        "label": "Load a device (instrument or audio effect) onto the selected track by name.",
        "params": [{"name": "name", "type": "str", "required": True}],
        "path": "/device/load",
        "method": "GET",
    },
]


def get_catalog() -> List[Dict[str, Any]]:
    return _CATALOG
