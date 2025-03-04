from _Framework.ButtonElement import ButtonElement
from _Framework.InputControlElement import MIDI_NOTE_TYPE, MIDI_CC_TYPE
from _Framework.SubjectSlot import subject_slot, SlotManager

from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.track_recorder.RecordService import RecordService
from protocol0.domain.track_recorder.RecordTypeEnum import RecordTypeEnum
from protocol0.domain.track_recorder.event.RecordEndedEvent import RecordEndedEvent
from protocol0.infra.midi.NoteSentEvent import NoteSentEvent
from protocol0.shared.Song import Song


class ActionGroupMC6Pro(ActionGroupInterface, SlotManager):
    CHANNEL = 2

    def configure(self) -> None:
        self.add_encoder(
            identifier=0,
            name="record first armed track",
            on_press=self.action_record_first_armed_track,
            use_note_off=True,
        )
        #
        self.add_encoder(
            identifier=1,
            name="record all armed tracks",
            on_press=self.action_record_armed_tracks,
        )

    def action_record_first_armed_track(self) -> None:
        if Song.is_session_recording():
            DomainEventBus.emit(RecordEndedEvent())
        else:
            first_armed_track = next(iter(Song.armed_tracks()), None)
            assert first_armed_track, "No track armed"
            self._container.get(RecordService).record_tracks(
                [first_armed_track], RecordTypeEnum.MIDI
            )

    def action_record_armed_tracks(self) -> None:
        if Song.is_session_recording():
            DomainEventBus.emit(RecordEndedEvent())
        else:
            self._container.get(RecordService).record_tracks(
                Song.armed_tracks(), RecordTypeEnum.MIDI
            )
