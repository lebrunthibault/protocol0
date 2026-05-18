import requests
from fastapi import HTTPException
from loguru import logger

from p0_backend.settings import Settings


class P0ScriptClient(object):
    _INSTANCE = None

    def __init__(self, base_url: str):
        self._base_url = base_url
        self._session = requests.Session()

    def _get(self, path: str, params: dict = None) -> None:
        url = self._base_url + path
        try:
            r = self._session.get(url, params=params, timeout=5)
            r.raise_for_status()
        except requests.RequestException as e:
            logger.warning(f"script HTTP {path} failed: {e}")
            raise HTTPException(status_code=503, detail=f"p0_script unreachable: {e}")

    def select_track(self, name: str) -> None:
        self._get("/track/select", {"name": name})

    def get_set_state(self) -> dict:
        url = self._base_url + "/set/get_state"
        try:
            r = self._session.get(url, timeout=5)
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            logger.warning(f"script HTTP /set/get_state failed: {e}")
            raise HTTPException(status_code=503, detail=f"p0_script unreachable: {e}")

    def toggle_follow_song(self) -> None:
        self._get("/song/toggle_follow")

    def on_key_detected(self, pitch: int) -> None:
        self._get("/clip/key_detected", {"pitch": pitch})


def p0_script_client() -> P0ScriptClient:
    if P0ScriptClient._INSTANCE is None:
        P0ScriptClient._INSTANCE = P0ScriptClient(Settings().p0_script_url)
    return P0ScriptClient._INSTANCE
