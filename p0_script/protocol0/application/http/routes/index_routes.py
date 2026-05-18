import html
import inspect

from protocol0.application.http.Router import get_routes, route


def _param_label(name: str, param: inspect.Parameter) -> str:
    annotation = param.annotation
    type_name = getattr(annotation, "__name__", "") if annotation is not inspect.Parameter.empty else ""
    suffix = "" if param.default is inspect.Parameter.empty else "?"
    return "%s%s%s" % (name, ":" + type_name if type_name else "", suffix)


def _row(method: str, path: str, fn) -> str:
    sig = inspect.signature(fn)
    params = [_param_label(n, p) for n, p in sig.parameters.items()]
    has_required = any(p.default is inspect.Parameter.empty for p in sig.parameters.values())
    params_html = ", ".join(html.escape(p) for p in params)
    path_html = html.escape(path)
    if method == "GET" and not has_required:
        path_cell = '<a href="%s">%s</a>' % (path_html, path_html)
    else:
        path_cell = path_html
    return "<tr><td>%s</td><td>%s</td><td>%s</td></tr>" % (method, path_cell, params_html)


@route("GET", "/")
def index() -> str:
    rows = "\n".join(
        _row(method, path, fn)
        for (method, path), fn in sorted(get_routes().items())
        if path != "/"
    )
    return (
        "<!doctype html><html><head><meta charset='utf-8'>"
        "<title>p0_script HTTP</title>"
        "<style>"
        "body{font-family:sans-serif;max-width:720px;margin:2em auto;padding:0 1em}"
        "table{border-collapse:collapse;width:100%}"
        "th,td{border-bottom:1px solid #ddd;padding:.4em .6em;text-align:left}"
        "th{background:#f4f4f4}"
        "code,a{font-family:monospace}"
        "</style></head><body>"
        "<h1>p0_script HTTP endpoints</h1>"
        "<table><thead><tr><th>Method</th><th>Path</th><th>Params</th></tr></thead>"
        "<tbody>" + rows + "</tbody></table>"
        "</body></html>"
    )
