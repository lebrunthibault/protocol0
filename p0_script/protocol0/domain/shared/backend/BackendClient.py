import json
import urllib.parse
import urllib.request
from typing import Any, List


class BackendClient(object):
    """HTTP client for the p0_backend FastAPI server.

    Only methods actually called from the script are listed here. To wire a new
    backend route, add a method next to the others — match the route's HTTP
    method, path, and payload shape (see p0_backend/.../routes/).
    """

    _BASE_URL = "http://127.0.0.1:8000"

    def _get(self, path, params=None):
        # type: (str, dict) -> None
        url = self._BASE_URL + path
        if params:
            url = url + "?" + urllib.parse.urlencode(params, doseq=True)
        self._send(urllib.request.Request(url, method="GET"))

    def _post(self, path, body):
        # type: (str, dict) -> None
        self._send(self._json_request(path, body, "POST"))

    def _put(self, path, body):
        # type: (str, dict) -> None
        self._send(self._json_request(path, body, "PUT"))

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
        # type: () -> None
        self._get("/ping")

    def tail_logs(self):
        # type: () -> None
        self._get("/tail_logs")

    def clear_state(self):
        # type: () -> None
        self._post("/set/clear_state", {})

    def show_info(self, message):
        # type: (str) -> None
        self._get("/show_info", {"message": message})

    def show_success(self, message):
        # type: (str) -> None
        self._get("/show_success", {"message": message})

    def show_warning(self, message):
        # type: (str) -> None
        self._get("/show_warning", {"message": message})

    def show_error(self, message):
        # type: (str) -> None
        self._get("/show_error", {"message": message})

    def load_device(self, name):
        # type: (str) -> None
        self._get("/device/load", {"name": name})

    def toggle_ableton_button(self, x, y):
        # type: (int, int) -> None
        self._get("/device/toggle_ableton_button", {"x": x, "y": y})

    def move_to(self, x, y):
        # type: (int, int) -> None
        self._get("/keyboard/move_to", {"x": x, "y": y})

    def scroll(self, pixels):
        # type: (int) -> None
        self._get("/keyboard/scroll", {"pixels": pixels})

    def post_analyze_key(self, notes):
        # type: (List[Any]) -> None
        self._post("/clip/analyze_key", {"notes": notes})

    def post_current_state(self, post_current_state_payload):
        # type: (Any) -> None
        self._post("/set/current_state", {"post_current_state_payload": post_current_state_payload})

    def update_track_color(self, update_track_color_payload):
        # type: (Any) -> None
        self._put("/set/track_color", {"update_track_color_payload": update_track_color_payload})
