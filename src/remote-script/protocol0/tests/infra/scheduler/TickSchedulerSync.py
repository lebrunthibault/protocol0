from typing import Callable, List

from protocol0.domain.shared.scheduler.TickSchedulerEventInterface import (
    TickSchedulerEventInterface,
)
from protocol0.domain.shared.scheduler.TickSchedulerInterface import TickSchedulerInterface


class TickSchedulerEventSync(TickSchedulerEventInterface):
    def __init__(self, callback: Callable, due_tick: int) -> None:
        self.callback = callback
        self.due_tick = due_tick
        self.cancelled = False

    def cancel(self) -> None:
        self.cancelled = True


class TickSchedulerSync(TickSchedulerInterface):
    """Deterministic tick scheduler for tests.

    Unlike TickSchedulerTest (threading.Timer based, wall-clock), callbacks stay
    queued until the test advances the clock explicitly, making deferred code
    paths (Scheduler.defer / wait, Sequence.defer) synchronous and assertable.
    The `unique` flag is ignored (no test relies on it yet).
    """

    def __init__(self) -> None:
        self._current_tick = 0
        self._pending: List[TickSchedulerEventSync] = []

    def schedule(
        self, tick_count: int, callback: Callable, unique: bool = False
    ) -> TickSchedulerEventSync:
        event = TickSchedulerEventSync(callback, self._current_tick + max(tick_count, 1))
        self._pending.append(event)
        return event

    def advance(self, ticks: int = 1) -> None:
        """Advance the clock, executing due callbacks. Callbacks scheduled while
        advancing land on later ticks (like the real 17ms tick loop)."""
        for _ in range(ticks):
            self._current_tick += 1
            due = [e for e in self._pending if e.due_tick <= self._current_tick]
            self._pending = [e for e in self._pending if e.due_tick > self._current_tick]
            for event in due:
                if not event.cancelled:
                    event.callback()

    def drain(self, max_ticks: int = 100) -> None:
        """Advance until nothing is pending (capped, in case a callback re-arms itself)."""
        ticks = 0
        while self._pending and ticks < max_ticks:
            self.advance()
            ticks += 1

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass
