from typing import Optional


class ErrorRaisedEvent(object):
    def __init__(self, context: Optional[str] = None) -> None:
        self.context = context
