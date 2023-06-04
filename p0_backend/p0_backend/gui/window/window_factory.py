from p0_backend.gui.window.window import Window
from p0_backend.lib.enum.notification_enum import NotificationEnum


class WindowFactory:
    @classmethod
    def createWindow(cls, message: str, notification_enum: NotificationEnum, **k) -> Window:
        raise NotImplementedError
