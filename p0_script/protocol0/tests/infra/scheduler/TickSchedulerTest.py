from typing import Callable

from protocol0.domain.shared.scheduler.TickSchedulerEventInterface import (
    TickSchedulerEventInterface,
)
from protocol0.domain.shared.scheduler.TickSchedulerInterface import TickSchedulerInterface
from protocol0.tests.infra.scheduler.TickSchedulerEventTest import TickSchedulerEventTest


class TickSchedulerTest(TickSchedulerInterface):
    """use threading instead of Live Timer"""

    def schedule(
        self, tick_count: int, callback: Callable, unique: bool = False
    ) -> TickSchedulerEventInterface:
        """timeout_duration in ms"""
        return TickSchedulerEventTest(callback, tick_count)

    def start(self) -> None:
        pass

    def stop(self):
        pass
