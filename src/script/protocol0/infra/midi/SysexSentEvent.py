from typing import Tuple


class SysexSentEvent(object):
    def __init__(self, message: Tuple[int, ...]):
        self.message = message
