from typing import Callable, Optional

from protocol0.domain.shared.scheduler.BeatSchedulerInterface import BeatSchedulerInterface
from protocol0.domain.shared.scheduler.TickSchedulerEventInterface import (
    TickSchedulerEventInterface,
)
from protocol0.domain.shared.scheduler.TickSchedulerInterface import TickSchedulerInterface
from protocol0.shared.Song import Song


class Scheduler(object):
    """Facade for scheduling calls"""

    _INSTANCE: Optional["Scheduler"] = None
    _TICKS_BY_SECOND = float(1000) / 17

    def __init__(self, tick_scheduler: TickSchedulerInterface, beat_scheduler: BeatSchedulerInterface) -> None:
        Scheduler._INSTANCE = self
        self._tick_scheduler = tick_scheduler
        self._beat_scheduler = beat_scheduler

    @classmethod
    def defer(cls, callback: Callable) -> None:
        cls._INSTANCE._tick_scheduler.schedule(1, callback)

    @classmethod
    def wait_beats(cls, beats: float, callback: Callable, execute_on_song_stop: bool = False) -> None:
        cls._INSTANCE._beat_scheduler.wait_beats(beats, callback, execute_on_song_stop)

    @classmethod
    def wait_bars(cls, bars: float, callback: Callable, execute_on_song_stop: bool = False) -> None:
        cls._INSTANCE._beat_scheduler.wait_beats(
            bars * Song.signature_numerator(), callback, execute_on_song_stop
        )

    @classmethod
    def wait(cls, tick_count: int, callback: Callable, unique: bool = False) -> TickSchedulerEventInterface:
        """
        tick_count ~= 17 ms
        unique: accept only one callback of a type. the next callback will cancel the
        previous one scheduling
        """
        return cls._INSTANCE._tick_scheduler.schedule(tick_count, callback, unique)

    @classmethod
    def wait_ms(cls, duration: int, callback: Callable, unique: bool = False) -> TickSchedulerEventInterface:
        duration_second = float(duration) / 1000
        return cls.wait(int(duration_second * cls._TICKS_BY_SECOND), callback, unique)

    @classmethod
    def restart(cls) -> None:
        from protocol0.shared.sequence.Sequence import Sequence

        Sequence.reset()
        cls._INSTANCE._tick_scheduler.start()
        cls._INSTANCE._beat_scheduler.reset()

    @classmethod
    def reset(cls) -> None:
        cls._INSTANCE._tick_scheduler.stop()
        cls._INSTANCE._beat_scheduler.reset()
