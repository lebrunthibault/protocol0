"""Catalogue des actions assignables à un raccourci, dérivé des @route.

Le frontend (M3) consomme ce catalogue pour proposer les actions et leurs
paramètres. On le dérive des routes déjà enregistrées (get_routes()) plutôt
que de maintenir une liste à part : une route = une action candidate, sa
signature = ses params, son getdoc = son libellé (cf. index_routes qui
introspecte déjà les routes pour son tableau HTML).

Proto : allow-list restreinte (load_device seul). Le namespace d'actions est
volontairement petit tant que le détecteur ne sait mapper qu'elle (cf.
detector.script_client.execute). On élargit l'allow-list au fur et à mesure
que le mapping côté détecteur s'étend.
"""
import inspect
from typing import Any, Dict, List

from protocol0.application.http.Router import get_routes

# Actions exposées au frontend. Clé = nom de la fonction @route (== binding.action).
# Garder en phase avec detector.script_client.execute.
_ALLOWED_ACTIONS = ("load_device",)


def _params(fn) -> List[Dict[str, Any]]:
    params = []
    for name, param in inspect.signature(fn).parameters.items():
        annotation = param.annotation
        type_name = (
            getattr(annotation, "__name__", None)
            if annotation is not inspect.Parameter.empty
            else None
        )
        params.append(
            {
                "name": name,
                "type": type_name,
                "required": param.default is inspect.Parameter.empty,
            }
        )
    return params


def _label(fn) -> str:
    """1re ligne du docstring (getdoc), ou le nom de la fonction à défaut."""
    doc = inspect.getdoc(fn)
    if doc:
        return doc.splitlines()[0]
    return fn.__name__


def get_catalog() -> List[Dict[str, Any]]:
    """Liste des actions assignables, dans l'ordre de l'allow-list."""
    by_name = {fn.__name__: (method, path, fn) for (method, path), fn in get_routes().items()}
    catalog = []
    for action in _ALLOWED_ACTIONS:
        entry = by_name.get(action)
        if entry is None:
            continue
        method, path, fn = entry
        catalog.append(
            {
                "name": action,
                "label": _label(fn),
                "params": _params(fn),
                "path": path,
                "method": method,
            }
        )
    return catalog
