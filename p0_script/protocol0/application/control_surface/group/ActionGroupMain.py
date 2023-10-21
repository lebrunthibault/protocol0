from functools import partial
from typing import Optional

from protocol0.application.ScriptResetActivatedEvent import ScriptResetActivatedEvent
from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface
from protocol0.domain.lom.set.MixingService import MixingService
from protocol0.domain.lom.song.components.TempoComponent import TempoComponent
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.track_recorder.RecordService import RecordService
from protocol0.domain.track_recorder.RecordTypeEnum import RecordTypeEnum
from protocol0.shared.Song import Song
from protocol0.shared.sequence.Sequence import Sequence


# noinspection SpellCheckingInspection
class ActionGroupMain(ActionGroupInterface):
    CHANNEL = 4

    def configure(self) -> None:
        def record_track(record_type: RecordTypeEnum) -> Optional[Sequence]:
            return self._container.get(RecordService).record_track(
                Song.current_track(), record_type
            )

        # TAP tempo encoder
        self.add_encoder(
            identifier=1,
            name="tap tempo",
            on_press=self._container.get(TempoComponent).tap,
            on_scroll=self._container.get(TempoComponent).scroll,
        )

        # INIT song encoder
        self.add_encoder(
            identifier=4,
            name="(re) initialize the script",
            on_press=partial(DomainEventBus.emit, ScriptResetActivatedEvent()),
        )

        # RECordAudio encoder
        self.add_encoder(
            identifier=5,
            name="record audio export",
            filter_active_tracks=True,
            on_press=lambda: partial(record_track, RecordTypeEnum.AUDIO),
            on_long_press=lambda: partial(record_track, RecordTypeEnum.AUDIO_FULL),
        )

        # RECord normal encoder
        self.add_encoder(
            identifier=9,
            name="record normal",
            filter_active_tracks=True,
            on_scroll=self._container.get(RecordService).recording_bar_length_scroller.scroll,
            on_press=lambda: partial(record_track, RecordTypeEnum.MIDI),
            on_long_press=lambda: partial(record_track, RecordTypeEnum.MIDI_UNLIMITED),
        )


        self.add_encoder(
            identifier=13, name="test", on_press=self.action_test
        )

        # VOLume encoder
        self.add_encoder(
            identifier=16,
            name="volume",
            on_scroll=self._container.get(MixingService).scroll_all_tracks_volume,
        )

    def action_test(self) -> None:
        device = Song.selected_device()
        device.is_collapsed = not device.is_collapsed