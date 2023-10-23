from typing import Optional

from win11toast import toast_async

from p0_backend.lib.enum.notification_enum import NotificationEnum
from p0_backend.lib.notification.notification.notification import Notification
from p0_backend.lib.notification.window_factory import WindowFactory


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
    async def show_error(cls, message: str):
        await toast_async(message)
