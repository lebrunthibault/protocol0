import json
import urllib.parse
import urllib.request
from typing import Any, List

from protocol0.shared.env import get as env_get


class BackendClient(object):
    """HTTP client for the p0_backend FastAPI server.

    Only methods actually called from the script are listed here. To wire a new
    backend route, add a method next to the others — match the route's HTTP
    method, path, and payload shape (see p0_backend/.../routes/).
    """

    _BASE_URL = "http://127.0.0.1:" + env_get("P0_BACKEND_PORT", "8000")

    def _get(self, path, params=None):
        # type: (str, dict) -> None
        url = self._BASE_URL + path
        if params:
            url = url + "?" + urllib.parse.urlencode(params, doseq=True)
        self._send(urllib.request.Request(url, method="GET"))

    def _post(self, path, body):
        # type: (str, dict) -> None
        self._send(self._json_request(path, body, "POST"))

    def _json_request(self, path, body, method):
        # type: (str, dict, str) -> urllib.request.Request
        return urllib.request.Request(
            self._BASE_URL + path,
            data=json.dumps(body).encode("utf-8"),
            method=method,
            headers={"Content-Type": "application/json"},
        )

    def _send(self, req):
        # type: (urllib.request.Request) -> None
        try:
            urllib.request.urlopen(req, timeout=5).close()
        except Exception as e:
            try:
                from protocol0.shared.logging.Logger import Logger

                Logger.warning("HTTP %s %s failed: %r" % (req.get_method(), req.full_url, e))
            except Exception:
                pass

    def ping(self):
        # type: () -> bool
        try:
            urllib.request.urlopen(self._BASE_URL + "/ping", timeout=2).close()
            return True
        except Exception:
            return False

    def post_analyze_key(self, notes):
        # type: (List[Any]) -> None
        self._post("/clip/analyze_key", {"notes": notes})
