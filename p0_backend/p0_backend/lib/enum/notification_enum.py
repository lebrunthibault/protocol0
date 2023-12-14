from enum import Enum


class NotificationEnum(Enum):
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"

    @property
    def icon(self) -> str:
        return {
            self.INFO: "info.ico",
            self.SUCCESS: "success.ico",
            self.WARNING: "warning.ico",
            self.ERROR: "error.ico",
        }[
            self  # type: ignore[index]
        ]
