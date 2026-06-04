"""Catalogue statique des actions assignables, servi à la SPA (/api/actions).

Statique (et non plus dérivé des @route du script) pour que le sélecteur d'action du
keymapper fonctionne SANS Ableton. Même forme JSON que l'ex-get_catalog() du script :
    { name, label, params: [{name, type, required}], path, method }

COUPLAGE : garder en phase avec agent.script_client.ScriptClient.execute — une action
listée ici doit être dispatchable là-bas. Le namespace est volontairement petit tant que
l'agent ne sait mapper que load_device ; on l'élargit au fur et à mesure.
"""
from typing import Any, Dict, List

# Smart actions: high-level Protocol0 commands dispatched to the script over HTTP.
_CATALOG: List[Dict[str, Any]] = [
    {
        "name": "load_device",
        "label": "Load a device (instrument or audio effect) onto the selected track by name.",
        "params": [{"name": "name", "type": "str", "required": True}],
        "path": "/device/load",
        "method": "GET",
    },
]

# `send_keys` is the action behind every Ableton-shortcut remap: pressing the user's
# combo replays a native Live shortcut (params.keys), injected locally by the agent
# (no HTTP). It's a separate family from smart actions and the UI offers it via the
# searchable Ableton catalog (ableton_shortcuts), not as a free-text param — so it is
# deliberately NOT in _CATALOG. Kept here as documentation of the contract.
SEND_KEYS_ACTION = "send_keys"


def get_catalog() -> List[Dict[str, Any]]:
    return _CATALOG
