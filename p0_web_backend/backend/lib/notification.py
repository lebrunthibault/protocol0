import time
from dataclasses import dataclass, field
from typing import Optional

from loguru import logger

try:
    from win11toast import notify as system_notify
except ImportError:

    def system_notify(title: str, body: str, **_):
        logger.info(f"{title}: {body}")


@dataclass
class Notification:
    title: str
    created_at: float = field(default_factory=lambda: time.time())

    def is_duplicate(self, title: str):
        return self.title == title and time.time() - self.created_at < 3


last_notification: Optional[Notification] = None


def notify(title: str, body: str = ""):
    global last_notification
    if last_notification and last_notification.is_duplicate(title):
        return

    last_notification = Notification(title)

    system_notify(title, body, duration="short")
