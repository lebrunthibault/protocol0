"""Catalogue d'actions dérivé de l'API REST du script (son /openapi.json).

Plus de liste statique : déposer un plugin `@action` dans le script le fait apparaître
ici automatiquement. L'agent proxie le catalogue (le frontend, servi sur :9010, ne peut
pas fetch le script sur un autre port — CORS), le transforme dans la forme attendue par
la SPA, et le sert sur /api/actions :

    { name, label, description, params: [{name, type, required}], path, method }

- `name`   : nom de la méthode @action (ex. "load_device").
- `label`  : `name` en Title Case (ex. "Load Device").
- `description` : le summary OpenAPI (1re ligne de docstring de la méthode).
- `params` : depuis le requestBody JSON (type JSON Schema: string/integer/number/boolean).
- `path`   : "/action/<plugin>/<method>" (sans le préfixe /api, porté par servers[].url).

Script injoignable / erreur réseau -> liste vide (l'UI keymapper est de toute façon
verrouillée quand le script n'est pas "ready").
"""
import logging
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger("agent")

# Timeout court : /openapi.json est local et rapide ; on ne veut jamais bloquer l'UI.
_TIMEOUT_S = 2


def _title_case(name: str) -> str:
    """"load_device" -> "Load Device"."""
    return " ".join(word.capitalize() for word in name.split("_"))


def _params_from_request_body(operation: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extrait [{name, type, required}] du requestBody JSON d'une opération OpenAPI."""
    schema = (
        operation.get("requestBody", {})
        .get("content", {})
        .get("application/json", {})
        .get("schema", {})
    )
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))
    return [
        {"name": name, "type": prop.get("type", "string"), "required": name in required}
        for name, prop in properties.items()
    ]


def _to_action_def(path: str, method: str, operation: Dict[str, Any]) -> Dict[str, Any]:
    name = path.rsplit("/", 1)[-1]  # /action/<plugin>/<method> -> <method>
    return {
        "name": name,
        "label": _title_case(name),
        "description": operation.get("summary", ""),
        "params": _params_from_request_body(operation),
        "path": path,
        "method": method.upper(),
    }


def fetch(script_url: str, session: Optional[requests.Session] = None) -> List[Dict[str, Any]]:
    """Catalogue des actions exposées par le script, ou [] si injoignable.

    Ne lit que les routes /action/* du /openapi.json (les actions de plugins) ; les routes
    techniques (/track/select…) ne sont pas des actions assignables côté keymapper.
    """
    getter = session.get if session is not None else requests.get
    try:
        r = getter(script_url + "/openapi.json", timeout=_TIMEOUT_S)
        r.raise_for_status()
        spec = r.json()
    except (requests.RequestException, ValueError) as e:
        logger.info("action catalog unavailable: %s" % e)
        return []

    catalog: List[Dict[str, Any]] = []
    for path, item in spec.get("paths", {}).items():
        if not path.startswith("/action/"):
            continue
        for method, operation in item.items():
            catalog.append(_to_action_def(path, method, operation))
    return catalog
