from threading import Timer

from typing import Callable

from protocol0.domain.shared.scheduler.TickSchedulerEventInterface import (
    TickSchedulerEventInterface,
)


class TickSchedulerEventTest(TickSchedulerEventInterface):
    def __init__(self, callback: Callable, tick_count: int) -> None:
        self._timer = Timer(float(tick_count) / 100, callback)
        self._timer.start()

    def cancel(self) -> None:
        self._timer.cancel()
