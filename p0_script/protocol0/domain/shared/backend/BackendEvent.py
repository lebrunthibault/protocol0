from typing import Any


class BackendEvent(object):
    def __init__(self, event: str, data: Any = None) -> None:
        self.event = event
        self.data = data
