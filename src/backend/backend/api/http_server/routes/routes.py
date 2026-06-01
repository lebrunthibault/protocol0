import html
import inspect

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRoute

from backend.version import __version__

from .clip_routes import router as clip_router

router = APIRouter()

router.include_router(clip_router, prefix="/clip")


def _params_label(route: APIRoute) -> str:
    sig = inspect.signature(route.endpoint)
    parts = []
    for name, param in sig.parameters.items():
        if name in ("request",):
            continue
        annotation = param.annotation
        type_name = (
            getattr(annotation, "__name__", "") if annotation is not inspect.Parameter.empty else ""
        )
        suffix = "" if param.default is inspect.Parameter.empty else "?"
        parts.append("%s%s%s" % (name, ":" + type_name if type_name else "", suffix))
    return ", ".join(parts)


def _row(route: APIRoute) -> str:
    method = ",".join(sorted(route.methods - {"HEAD"})) or "GET"
    path_html = html.escape(route.path)
    params_html = html.escape(_params_label(route))
    has_required = any(
        p.default is inspect.Parameter.empty and n != "request"
        for n, p in inspect.signature(route.endpoint).parameters.items()
    )
    if method == "GET" and not has_required:
        path_cell = '<a href="%s">%s</a>' % (path_html, path_html)
    else:
        path_cell = path_html
    desc_html = html.escape(inspect.getdoc(route.endpoint) or "")
    return "<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (
        method,
        path_cell,
        params_html,
        desc_html,
    )


@router.get("/", response_class=HTMLResponse)
def home(request: Request) -> str:
    """Render an HTML index of every registered HTTP endpoint."""
    routes = sorted(
        (r for r in request.app.routes if isinstance(r, APIRoute)),
        key=lambda r: r.path,
    )
    rows = "\n".join(_row(r) for r in routes)
    return (
        "<!doctype html><html><head><meta charset='utf-8'>"
        "<title>backend HTTP</title>"
        "<style>"
        "body{font-family:sans-serif;max-width:960px;margin:2em auto;padding:0 1em}"
        "table{border-collapse:collapse;width:100%}"
        "th,td{border-bottom:1px solid #ddd;padding:.4em .6em;text-align:left}"
        "th{background:#f4f4f4}"
        "code,a{font-family:monospace}"
        "</style></head><body>"
        "<h1>backend HTTP endpoints "
        "<small style='color:#888;font-weight:normal'>v" + __version__ + "</small></h1>"
        "<table><thead><tr><th>Method</th><th>Path</th><th>Params</th><th>Description</th></tr></thead>"
        "<tbody>" + rows + "</tbody></table>"
        "</body></html>"
    )


@router.get("/ping")
def ping() -> str:
    """Health-check endpoint that returns the literal string "pong"."""
    return "pong"
