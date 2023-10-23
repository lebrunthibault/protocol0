from enum import Enum
from typing import cast

from p0_backend.lib.enum.color_enum import ColorEnum


class NotificationEnum(Enum):
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"

    @property
    def color(self) -> ColorEnum:
        return cast(
            ColorEnum,
            {
                NotificationEnum.INFO: ColorEnum.INFO,
                NotificationEnum.SUCCESS: ColorEnum.SUCCESS,
                NotificationEnum.WARNING: ColorEnum.WARNING,
                NotificationEnum.ERROR: ColorEnum.ERROR,
            }.get(self),
        )

    @property
    def icon(self) -> str:
        return {
            self.INFO: "info.ico",
            self.SUCCESS: "success.ico",
            self.WARNING: "warning.ico",
            self.ERROR: "error.ico",
        }[self]  # type: ignore[index]
