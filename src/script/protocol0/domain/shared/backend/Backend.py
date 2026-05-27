from typing import Optional

from protocol0.domain.shared.backend.BackendClient import BackendClient


class Backend(object):
    """Backend API facade"""

    _INSTANCE: Optional["Backend"] = None

    def __init__(self) -> None:
        Backend._INSTANCE = self
        self._client = BackendClient()

    @classmethod
    def client(cls) -> BackendClient:
        return cls._INSTANCE._client
