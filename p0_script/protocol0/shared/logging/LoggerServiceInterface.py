from typing import Any, Optional

from protocol0.shared.logging.LogLevelEnum import LogLevelEnum


class LoggerServiceInterface(object):
    def log(self, message: Any, debug: bool = True, level: Optional[LogLevelEnum] = None) -> None:
        pass
