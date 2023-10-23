from win11toast import notify

from p0_backend.lib.enum.notification_enum import NotificationEnum
from p0_backend.settings import Settings


class NotificationWindowTask:
    def delay(self, title: str, level: NotificationEnum = NotificationEnum.INFO, body: str = ""):
        notify(title, body, icon=f"{Settings().icons_directory}\\{level.icon}", duration="short")


notification_window = NotificationWindowTask()


def create_app():
    pass
