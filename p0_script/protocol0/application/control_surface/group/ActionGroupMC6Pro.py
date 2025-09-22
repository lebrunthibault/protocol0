from functools import partial

from _Framework.ButtonElement import ButtonElement
from _Framework.InputControlElement import MIDI_NOTE_TYPE, MIDI_CC_TYPE
from _Framework.SubjectSlot import subject_slot, SlotManager

from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.BarChangedEvent import BarChangedEvent
from protocol0.domain.track_recorder.RecordService import RecordService
from protocol0.domain.track_recorder.RecordTypeEnum import RecordTypeEnum
from protocol0.domain.track_recorder.event.RecordEndedEvent import RecordEndedEvent
from protocol0.infra.midi.MidiService import MidiService
from protocol0.shared.Song import Song
from protocol0.shared.sequence.Sequence import Sequence


class ActionGroupMC6Pro(ActionGroupInterface, SlotManager):
    CHANNEL = 12

    def configure(self) -> None:
        self.add_encoder(identifier=1, name="capture midi", on_press=self.capture_midi)

    def capture_midi(self) -> None:
        seq = Sequence()
        seq.add(Song.capture_midi)
        seq.add(partial(self._container.get(MidiService).send_ec4_select_group, 9))
        seq.wait_for_event(BarChangedEvent)

        def set_clips_loop() -> None:
            for track in Song.armed_tracks():
                if track.playing_clip and track.playing_clip.bar_length:
                    track.playing_clip.loop.bar_length = 4

        seq.add(set_clips_loop)
        seq.done()

    def launch_drop(self) -> None:
        from protocol0.shared.logging.Logger import Logger

        Logger.dev("launch drop")
        pass
