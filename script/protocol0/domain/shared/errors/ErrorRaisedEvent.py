from typing import Optional


class ErrorRaisedEvent(object):
    def __init__(self, context: Optional[str] = None, reset: bool = True) -> None:
        self.context = context
        self.reset = reset
