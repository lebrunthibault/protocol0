"""Routes techniques de l'API : santé, doc, racine.

L'API du script est une vraie API REST JSON : la racine ne sert plus de HTML
(l'ancienne page d'index a disparu), elle redirige vers la Swagger UI. La surface
humaine, c'est /docs ; la surface machine, c'est /openapi.json (généré depuis le
registre de routes). Voir docs/specs/.../2026-06-04-script-rest-api-and-swagger.md.
"""
from protocol0.application.http import openapi, swagger_ui
from protocol0.application.http.Router import Response, api_route, route
from protocol0.version import __version__


@api_route("GET", "/health")
def health() -> dict:
    """Liveness probe (cible de ping non ambiguë pour la page web de l'agent)."""
    return {"ok": True, "version": __version__}


@route("GET", "/")
def index() -> Response:
    """Redirige vers la Swagger UI (l'API ne sert pas de HTML à la racine)."""
    return Response.redirect("/docs")


@route("GET", "/openapi.json")
def openapi_json() -> Response:
    """Document OpenAPI 3.1 décrivant toute l'API (routes core + plugins)."""
    return Response.json(openapi.build_spec())


@route("GET", "/docs")
def docs() -> Response:
    """Swagger UI (vendorée, offline) — la surface humaine de l'API."""
    served = swagger_ui.resolve("/docs")
    if served is None:
        return Response.bytes(b"swagger ui not found", "text/plain; charset=utf-8", 500)
    body, content_type = served
    return Response.bytes(body, content_type)
