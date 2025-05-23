import Live

from protocol0.domain.lom.clip.ClipEnvelopeShowedEvent import ClipEnvelopeShowedEvent
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.utils.timing import defer
from protocol0.domain.track_recorder.event.RecordEndedEvent import RecordEndedEvent
from protocol0.domain.track_recorder.event.RecordStartedEvent import RecordStartedEvent


class RecordingComponent(object):
    def __init__(self, song: Live.Song.Song) -> None:
        self._live_song = song
        DomainEventBus.subscribe(ClipEnvelopeShowedEvent, lambda _: song.re_enable_automation())
        DomainEventBus.subscribe(RecordStartedEvent, self._on_record_started_event)
        DomainEventBus.subscribe(RecordEndedEvent, self._on_record_ended_event)

    @defer
    def _on_record_started_event(self, _: RecordStartedEvent) -> None:
        self.session_automation_record = True
        # self.session_record = True

    def _on_record_ended_event(self, _: RecordEndedEvent) -> None:
        self.session_automation_record = False
        self.session_record = False

    @property
    def back_to_arranger(self) -> bool:
        return self._live_song.back_to_arranger

    @back_to_arranger.setter
    def back_to_arranger(self, back_to_arranger: bool) -> None:
        self._live_song.back_to_arranger = back_to_arranger

    @property
    def session_record(self) -> bool:
        return self._live_song.session_record

    @session_record.setter
    def session_record(self, session_record: bool) -> None:
        self._live_song.session_record = session_record

    @property
    def session_automation_record(self) -> bool:
        return self._live_song.session_automation_record

    @session_automation_record.setter
    def session_automation_record(self, session_automation_record: bool) -> None:
        self._live_song.session_automation_record = session_automation_record
