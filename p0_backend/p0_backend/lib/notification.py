import time
from dataclasses import dataclass, field
from typing import Optional

from win11toast import notify as win11toast_notify

from p0_backend.lib.enum.notification_enum import NotificationEnum
from p0_backend.settings import Settings


@dataclass
class Notification:
    title: str
    created_at: float = field(default_factory=lambda: time.time())

    def is_duplicate(self, title: str):
        return self.title == title and time.time() - self.created_at < 3


last_notification: Optional[Notification] = None


def notify(title: str, level: NotificationEnum = None, body: str = ""):
    global last_notification
    if last_notification and last_notification.is_duplicate(title):
        return

    last_notification = Notification(title)

    if level and level == NotificationEnum.ERROR:
        win11toast_notify(
            title, body, icon=f"{Settings().icons_directory}\\{level.icon}", duration="short"
        )
    else:
        win11toast_notify(title, body, duration="short")
