from threading import Timer
from typing import Callable


def start_timer(interval: float, function: Callable) -> Timer:
    t = Timer(interval, function)
    t.daemon = True
    t.start()

    return t
