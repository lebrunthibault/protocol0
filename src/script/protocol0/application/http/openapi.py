"""Génère un document OpenAPI 3.1 à la volée depuis le registre de routes.

Pas de YAML statique à maintenir (contrairement à Jupyter) : on introspecte
``get_routes()`` — method, path, signature, docstring — comme le faisait l'ancienne
page d'index HTML. Les routes de plugins (déclarées via ``@api_route`` dans
``register_actions``) apparaissent donc automatiquement dans /openapi.json et donc
dans la Swagger UI.

Stdlib-only (Ableton) : juste ``inspect`` + des dicts. La fidélité des schémas est
volontairement minimale (une API d'actions n'a pas besoin de schémas riches) :
on expose nom/type/required/description, ce que l'introspection donne déjà.
"""
import inspect
from typing import Any, Callable, Dict

from protocol0.application.http.Router import API_PREFIX, get_routes
from protocol0.version import __version__

# Routes techniques exclues du contrat d'API (ce sont la doc et la racine,
# pas des endpoints d'action).
_HIDDEN_PATHS = {"/", "/docs", "/openapi.json"}

# Mapping annotation Python -> type JSON Schema. Tout le reste tombe sur "string".
_JSON_TYPE = {int: "integer", bool: "boolean", float: "number", str: "string"}


def _json_type(annotation: type) -> str:
    return _JSON_TYPE.get(annotation, "string")


def _param_schema(param: inspect.Parameter) -> Dict[str, Any]:
    annotation = param.annotation
    type_name = _json_type(annotation) if annotation is not inspect.Parameter.empty else "string"
    return {"type": type_name}


def _operation(method: str, fn: Callable) -> Dict[str, Any]:
    """Construit l'Operation Object OpenAPI d'une route. GET -> parameters (query) ;
    POST/PUT/PATCH -> requestBody JSON (les mutations passent leurs args en body)."""
    sig = inspect.signature(fn)
    doc = inspect.getdoc(fn) or ""
    summary = doc.splitlines()[0] if doc else fn.__name__

    op: Dict[str, Any] = {"summary": summary, "responses": {"200": {"description": "OK"}}}
    if doc:
        op["description"] = doc

    params = list(sig.parameters.items())
    if not params:
        return op

    if method == "GET":
        op["parameters"] = [
            {
                "name": name,
                "in": "query",
                "required": param.default is inspect.Parameter.empty,
                "schema": _param_schema(param),
            }
            for name, param in params
        ]
    else:
        properties = {name: _param_schema(param) for name, param in params}
        required = [
            name for name, param in params if param.default is inspect.Parameter.empty
        ]
        schema: Dict[str, Any] = {"type": "object", "properties": properties}
        if required:
            schema["required"] = required
        op["requestBody"] = {
            "required": bool(required),
            "content": {"application/json": {"schema": schema}},
        }
    return op


def build_spec() -> Dict[str, Any]:
    """Document OpenAPI 3.1 complet, dérivé du registre courant."""
    paths: Dict[str, Dict[str, Any]] = {}
    for (method, path), fn in sorted(get_routes().items()):
        if path in _HIDDEN_PATHS:
            continue
        paths.setdefault(path, {})[method.lower()] = _operation(method, fn)

    return {
        "openapi": "3.1.0",
        "info": {
            "title": "Protocol 0 — script API",
            "description": (
                "Localhost HTTP API exposed by the Protocol 0 remote script inside "
                "Ableton Live. Drives Live directly; the same calls a keyboard "
                "shortcut makes under the hood."
            ),
            "version": __version__,
        },
        "servers": [{"url": API_PREFIX, "description": "Action API"}],
        "paths": _strip_prefix(paths),
    }


def _strip_prefix(paths: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Les routes sont enregistrées avec le préfixe /api (via @api_route). Comme on
    déclare ``servers: [{url: /api}]``, on retire le préfixe des chemins pour ne pas
    le dupliquer (OpenAPI préfixe déjà chaque path par l'URL du serveur)."""
    out: Dict[str, Dict[str, Any]] = {}
    for path, item in paths.items():
        key = path[len(API_PREFIX):] if path.startswith(API_PREFIX + "/") else path
        out[key] = item
    return out
