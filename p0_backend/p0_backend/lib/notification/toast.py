from win10toast import ToastNotifier

from p0_backend.lib.enum.notification_enum import NotificationEnum
from p0_backend.settings import Settings

toast = ToastNotifier()

settings = Settings()


def show_notification(title: str, body: str, level: NotificationEnum):
    toast.show_toast(
        title,
        body,
        icon_path=f"{settings.icons_directory}\\{level.icon}",
        duration=3,
        threaded=True,
    )
