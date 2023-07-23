from loguru import logger

from p0_backend.lib.notification.toast import show_notification


class CeleryTaskStub:
    def __init__(self, name: str):
        self._name = name

    def delay(self, *a, **k):
        logger.info("{} called with args: {}, kwargs: {}".format(self._name, a, k))

        if self._name == "notification_window":
            show_notification(a[0])


notification_window = CeleryTaskStub("notification_window")
select_window = CeleryTaskStub("select_window")


def create_app():
    pass


def check_celery_worker_status():
    return True
