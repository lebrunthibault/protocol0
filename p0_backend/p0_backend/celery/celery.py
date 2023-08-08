from p0_backend.lib.enum.notification_enum import NotificationEnum
from p0_backend.lib.notification.toast import show_notification


class NotificationWindowTask:
    def delay(self, title: str, level: NotificationEnum = NotificationEnum.INFO, body: str = ""):
        show_notification(title, body, level)


notification_window = NotificationWindowTask()


def create_app():
    pass


def check_celery_worker_status():
    return True
