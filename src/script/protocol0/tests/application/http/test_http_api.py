"""Tests de l'API REST du script : routage /api, génération OpenAPI, Swagger UI.

L'import de ``protocol0.tests`` (paquet parent) câble les stubs _Framework via
``monkey_patch_static`` — nécessaire car importer le paquet ``routes`` tire des
modules dépendants de l'API Live (device_routes, clip_routes)."""
import json

import protocol0.tests  # noqa: F401  (déclenche monkey_patch_static au collect)
from protocol0.application.http import openapi, swagger_ui
from protocol0.application.http.Router import (
    API_PREFIX,
    Response,
    _build_kwargs,
    _coerce,
    api_route,
    get_routes,
    route,
)


def _import_routes() -> None:
    # Enregistre toutes les routes (core + plugins) via les décorateurs.
    import protocol0.application.http.routes  # noqa: F401


# --- prefix / enregistrement ------------------------------------------------


def test_api_route_prefixes_path() -> None:
    @api_route("POST", "/zzz_test/thing")
    def _thing() -> None:
        pass

    assert ("POST", API_PREFIX + "/zzz_test/thing") in get_routes()


def test_route_keeps_exact_path() -> None:
    @route("GET", "/zzz_exact")
    def _exact() -> Response:
        return Response.json({})

    assert ("GET", "/zzz_exact") in get_routes()


def test_action_routes_live_under_api_and_use_post() -> None:
    _import_routes()
    routes = get_routes()
    # Mutations -> POST sous /api.
    assert ("POST", "/api/track/select") in routes
    assert ("POST", "/api/song/toggle_follow") in routes
    assert ("POST", "/api/clip/key_detected") in routes
    # Lecture pure -> GET.
    assert ("GET", "/api/set/get_state") in routes
    assert ("GET", "/api/health") in routes
    # Plus aucune action en GET à la racine (l'ancienne forme a disparu).
    assert ("GET", "/track/select") not in routes


def test_technical_routes_registered() -> None:
    _import_routes()
    routes = get_routes()
    assert ("GET", "/") in routes
    assert ("GET", "/docs") in routes
    assert ("GET", "/openapi.json") in routes


# --- coercition des params --------------------------------------------------


def test_coerce_primitives() -> None:
    assert _coerce("42", int) == 42
    assert _coerce("true", bool) is True
    assert _coerce("no", bool) is False
    assert _coerce("kick", str) == "kick"


def test_build_kwargs_from_get_query_coerces_str() -> None:
    def fn(pitch: int) -> None:
        pass

    assert _build_kwargs(fn, {"pitch": "60"}) == {"pitch": 60}


def test_build_kwargs_from_post_body_keeps_types() -> None:
    def fn(pitch: int) -> None:
        pass

    # Un body JSON arrive déjà typé : pas de re-coercition d'un int.
    assert _build_kwargs(fn, {"pitch": 60}) == {"pitch": 60}


def test_build_kwargs_missing_required_raises() -> None:
    def fn(name: str) -> None:
        pass

    try:
        _build_kwargs(fn, {})
        assert False, "expected ValueError"
    except ValueError:
        pass


# --- OpenAPI ----------------------------------------------------------------


def test_openapi_is_3_1_with_server_prefix() -> None:
    _import_routes()
    spec = openapi.build_spec()
    assert spec["openapi"] == "3.1.0"
    assert spec["servers"] == [{"url": API_PREFIX, "description": "Action API"}]
    assert "version" in spec["info"]


def test_openapi_lists_actions_without_double_prefix() -> None:
    _import_routes()
    spec = openapi.build_spec()
    paths = spec["paths"]
    # Le préfixe /api est porté par servers[].url -> il est retiré des paths.
    assert "/track/select" in paths
    assert "/api/track/select" not in paths
    assert "post" in paths["/track/select"]


def test_openapi_post_uses_request_body_get_uses_params() -> None:
    _import_routes()
    paths = openapi.build_spec()["paths"]
    # track/select (POST, param name) -> requestBody JSON requis.
    select = paths["/track/select"]["post"]
    schema = select["requestBody"]["content"]["application/json"]["schema"]
    assert schema["properties"]["name"]["type"] == "string"
    assert "name" in schema["required"]
    # set/get_state (GET, sans param) -> pas de parameters.
    assert "parameters" not in paths["/set/get_state"]["get"]


def test_openapi_hides_technical_routes() -> None:
    _import_routes()
    paths = openapi.build_spec()["paths"]
    for hidden in ("/", "/docs", "/openapi.json"):
        assert hidden not in paths


def test_openapi_is_json_serializable() -> None:
    _import_routes()
    # Doit pouvoir être sérialisé tel quel par /openapi.json.
    json.dumps(openapi.build_spec())


# --- Response helpers -------------------------------------------------------


def test_response_redirect() -> None:
    r = Response.redirect("/docs")
    assert r.status == 302
    assert r.headers["Location"] == "/docs"


def test_response_json() -> None:
    r = Response.json({"ok": True})
    assert r.status == 200
    assert json.loads(r.body) == {"ok": True}
    assert "application/json" in r.headers["Content-Type"]


# --- Swagger UI vendorée ----------------------------------------------------


def test_swagger_ui_index_served() -> None:
    served = swagger_ui.resolve("/docs")
    assert served is not None
    body, ctype = served
    assert b"swagger-ui" in body.lower()
    assert ctype.startswith("text/html")


def test_swagger_ui_assets_served() -> None:
    css = swagger_ui.resolve("/docs/swagger-ui.css")
    js = swagger_ui.resolve("/docs/swagger-ui-bundle.js")
    assert css is not None and js is not None
    assert css[1].startswith("text/css")


def test_swagger_ui_rejects_path_traversal() -> None:
    assert swagger_ui.resolve("/docs/../Router.py") is None


def test_swagger_ui_missing_asset_is_none() -> None:
    assert swagger_ui.resolve("/docs/nope.js") is None
