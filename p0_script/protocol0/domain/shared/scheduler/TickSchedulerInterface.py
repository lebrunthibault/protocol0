from typing import Callable

from protocol0.domain.shared.scheduler.TickSchedulerEventInterface import (
    TickSchedulerEventInterface,
)


class TickSchedulerInterface(object):
    def schedule(self, tick_count: int, callback: Callable, unique: bool = False) -> TickSchedulerEventInterface:
        """timeout_duration in ms"""
        raise NotImplementedError

    def start(self) -> None:
        raise NotImplementedError

    def stop(self) -> None:
        raise NotImplementedError
