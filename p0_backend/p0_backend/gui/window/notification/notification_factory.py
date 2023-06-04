from typing import Optional

from p0_backend.gui.window.notification.notification import Notification
from p0_backend.gui.window.window_factory import WindowFactory
from p0_backend.lib.enum.notification_enum import NotificationEnum


class NotificationFactory(WindowFactory):
    BASE_SECOND_DURATION = 2
    CHAR_SECOND_DURATION = 0.05

    @classmethod
    def createWindow(
        cls,
        message: str,
        notification_enum: NotificationEnum = NotificationEnum.INFO,
        centered=False,
        auto_close_duration: Optional[float] = None,
    ) -> Notification:
        auto_close_duration = auto_close_duration or (
            cls.BASE_SECOND_DURATION + len(message) * cls.CHAR_SECOND_DURATION
        )
        return Notification(
            message=message,
            background_color=notification_enum.color,
            centered=centered,
            timeout=auto_close_duration,
            autofocus=notification_enum == NotificationEnum.ERROR,
        )

    @classmethod
    def show_error(cls, message: str):
        cls.createWindow(message=message, notification_enum=NotificationEnum.ERROR).display()
