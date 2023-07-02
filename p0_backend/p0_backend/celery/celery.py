from loguru import logger


class CeleryTaskStub:
    def __init__(self, name: str):
        self._name = name

    def delay(self, *a, **k):
        logger.info("{} called with args: {}, kwargs: {}".format(self._name, a, k))

notification_window = CeleryTaskStub("notification_window")
select_window = CeleryTaskStub("select_window")

def create_app():
    pass

def check_celery_worker_status():
    return True
