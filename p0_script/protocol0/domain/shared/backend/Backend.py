from functools import wraps
from typing import Optional, Any

from protocol0.domain.shared.backend.BackendClient import BackendClient

from protocol0.shared.logging.Logger import Logger
from protocol0.shared.types import Func


def show_and_log(backend_client_func: Func, log_func: Func) -> Func:
    @wraps(backend_client_func)
    def decorate(message: str, *a: Any, **k: Any) -> None:
        log_func(message)
        backend_client_func(message, *a, **k)

    return decorate


class Backend(object):
    """Backend API facade"""

    _INSTANCE: Optional["Backend"] = None

    def __init__(self) -> None:
        Backend._INSTANCE = self
        self._client = BackendClient()

        # wrap backend notification to also log
        self._client.show_info = show_and_log(self._client.show_info, Logger.info)
        self._client.show_success = show_and_log(self._client.show_success, Logger.info)
        self._client.show_warning = show_and_log(self._client.show_warning, Logger.warning)
        self._client.show_error = show_and_log(self._client.show_error, Logger.warning)

    @classmethod
    def client(cls) -> BackendClient:
        return cls._INSTANCE._client
