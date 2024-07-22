import Live
from typing import List, Callable, Optional

from protocol0.domain.shared.errors.error_handler import handle_errors
from protocol0.domain.shared.scheduler.TickSchedulerEventInterface import (
    TickSchedulerEventInterface,
)
from protocol0.domain.shared.scheduler.TickSchedulerInterface import TickSchedulerInterface
from protocol0.domain.shared.utils.func import is_func_equal
from protocol0.infra.scheduler.BeatScheduler import BeatScheduler
from protocol0.infra.scheduler.TickSchedulerEvent import TickSchedulerEvent
from protocol0.shared.logging.Logger import Logger


class TickScheduler(TickSchedulerInterface):
    def __init__(self, beat_scheduler: BeatScheduler, song: Live.Song.Song) -> None:
        self._beat_scheduler = beat_scheduler
        self._song = song
        self._live_timer: Optional[Live.Base.Timer] = None
        # noinspection PyArgumentList
        self._scheduled_events: List[TickSchedulerEvent] = []

        self.start()

    def stop(self) -> None:
        if self._live_timer:
            del self._scheduled_events[:]
            # noinspection PyArgumentList
            self._live_timer.stop()

    def start(self) -> None:
        self.stop()
        self._live_timer = Live.Base.Timer(callback=self._on_tick, interval=1, repeat=True)
        # noinspection PyArgumentList
        self._live_timer.start()

    @handle_errors()
    def _on_tick(self) -> None:
        # noinspection PyBroadException
        try:
            # this throws on startup
            is_song_playing = self._song.is_playing
        except Exception:
            return

        if is_song_playing:
            self._beat_scheduler._on_tick()
        for scheduled_event in self._scheduled_events[:]:
            if scheduled_event.should_execute:
                scheduled_event.execute()
                try:
                    self._scheduled_events.remove(scheduled_event)
                except ValueError:
                    pass
            else:
                scheduled_event.decrement_timeout()

    def schedule(
        self, tick_count: int, callback: Callable, unique: bool = False
    ) -> TickSchedulerEventInterface:
        assert callable(callback), "callback is not callable"
        assert tick_count > 0, "ticks_count is <= 0"

        if unique:
            for event in self._scheduled_events:
                if is_func_equal(event.callback, callback):
                    Logger.warning(
                        "Cancelling duplicate callback : %s -> %s" % (event.callback, callback)
                    )
                    event.cancel()
                    self._scheduled_events.remove(event)

        scheduled_event = TickSchedulerEvent(callback=callback, tick_count=tick_count)
        self._scheduled_events.append(scheduled_event)
        return scheduled_event
