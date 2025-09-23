import Live
from _Framework.SubjectSlot import subject_slot, SlotManager

from protocol0.domain.lom.song.SongStartedEvent import SongStartedEvent
from protocol0.domain.lom.song.SongStoppedEvent import SongStoppedEvent
from protocol0.domain.shared.ApplicationView import ApplicationView
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.track_recorder.event.RecordCancelledEvent import (
    RecordCancelledEvent,
)
from protocol0.domain.track_recorder.event.RecordEndedEvent import RecordEndedEvent
from protocol0.shared.Song import Song
from protocol0.shared.sequence.Sequence import Sequence


class PlaybackComponent(SlotManager):
    _DEBUG = False

    def __init__(self, song: Live.Song.Song) -> None:
        super(PlaybackComponent, self).__init__()
        self._live_song = song
        self._is_playing = (
            False  # caching this because _is_playing_listener activates multiple times
        )
        # self._is_playing_listener.subject = self._live_song
        DomainEventBus.subscribe(RecordEndedEvent, self._on_record_ended_event)
        DomainEventBus.subscribe(RecordCancelledEvent, self._on_record_cancelled_event)
        DomainEventBus.subscribe(SongStoppedEvent, self._on_song_stopped_event)

    @subject_slot("is_playing")
    def _is_playing_listener(self) -> None:
        # deduplicate calls with is_playing True
        if self.is_playing == self._is_playing:
            return
        else:
            self._is_playing = self.is_playing

        import logging

        logging.getLogger(__name__).info(self.is_playing)
        if not self.is_playing:
            DomainEventBus.defer_emit(SongStoppedEvent())
            self.stop()
        else:
            if ApplicationView.is_session_visible():
                self.re_enable_automation()

            DomainEventBus.defer_emit(SongStartedEvent())

    def _on_record_ended_event(self, _: RecordEndedEvent) -> None:
        pass
        # self.metronome = False
        # self.stop_playing()
        # # this is delayed in the case an encoder is touched after the recording is finished by mistake
        # for tick in [1, 10, 50, 100]:
        #     Scheduler.wait(tick, self.re_enable_automation)

    def _on_record_cancelled_event(self, _: RecordCancelledEvent) -> None:
        self.metronome = False
        self._live_song.stop_playing()

    def _on_song_stopped_event(self, _: SongStoppedEvent) -> None:
        self.metronome = False

    @property
    def is_playing(self) -> bool:
        return self._live_song.is_playing

    @is_playing.setter
    def is_playing(self, is_playing: bool) -> None:
        self._live_song.is_playing = is_playing

    def start_playing(self) -> None:
        self._live_song.is_playing = True

    def stop(self) -> Sequence:
        self.stop_all_clips(quantized=False)
        self.stop_playing()

        seq = Sequence()
        if Song.is_playing():
            seq.wait_for_event(SongStoppedEvent)
        return seq.done()

    def stop_playing(self) -> None:
        self._live_song.stop_playing()

    def stop_all_clips(self, quantized: bool = True) -> None:
        # noinspection PyTypeChecker
        self._live_song.stop_all_clips(quantized)

    def play_pause(self) -> None:
        if self.is_playing:
            self.stop_playing()
        else:
            self.start_playing()

    def restart(self) -> None:
        self.stop_playing()
        Scheduler.defer(self.start_playing)

    def reset(self) -> None:
        """stopping immediately"""
        self.stop_playing()
        # noinspection PyPropertyAccess
        self._live_song.current_song_time = 0
        self.stop_all_clips()

    @property
    def metronome(self) -> bool:
        return self._live_song.metronome

    @metronome.setter
    def metronome(self, metronome: bool) -> None:
        self._live_song.metronome = metronome

    def re_enable_automation(self) -> None:
        self._live_song.re_enable_automation()
