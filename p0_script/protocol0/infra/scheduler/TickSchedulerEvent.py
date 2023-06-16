from typing import Callable

from protocol0.domain.shared.scheduler.TickSchedulerEventInterface import (
    TickSchedulerEventInterface,
)
from protocol0.domain.shared.utils.func import get_callable_repr


class TickSchedulerEvent(TickSchedulerEventInterface):
    def __init__(self, callback: Callable, tick_count: int) -> None:
        self.callback = callback
        self._ticks_left = tick_count
        self._cancelled = False

    def __repr__(self) -> str:
        return get_callable_repr(self.callback)

    @property
    def should_execute(self) -> bool:
        return self._ticks_left == 0

    def decrement_timeout(self) -> None:
        assert self._ticks_left > 0, "0 ticks left"
        self._ticks_left -= 1

    def execute(self) -> None:
        if not self._cancelled:
            self.callback()

    def cancel(self) -> None:
        self._cancelled = True
