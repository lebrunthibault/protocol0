from functools import partial
from typing import Optional

from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface
from protocol0.domain.track_recorder.RecordService import RecordService
from protocol0.domain.track_recorder.RecordTypeEnum import RecordTypeEnum
from protocol0.shared.Song import Song
from protocol0.shared.sequence.Sequence import Sequence


# noinspection SpellCheckingInspection
class ActionGroupExt(ActionGroupInterface):
    CHANNEL = 12

    def configure(self) -> None:
        def record_track(record_type: RecordTypeEnum) -> Optional[Sequence]:
            return self._container.get(RecordService).record_track(
                Song.current_track(), record_type
            )

        # RECordAudio encoder
        self.add_encoder(
            identifier=1,
            name="record audio export",
            filter_active_tracks=True,
            on_press=lambda: partial(record_track, RecordTypeEnum.AUDIO),
            on_long_press=lambda: partial(record_track, RecordTypeEnum.AUDIO_FULL),
        )

        # RECord normal encoder
        self.add_encoder(
            identifier=2,
            name="record normal",
            filter_active_tracks=True,
            on_scroll=self._container.get(RecordService).recording_bar_length_scroller.scroll,
            on_press=lambda: partial(record_track, RecordTypeEnum.MIDI),
            on_long_press=lambda: partial(record_track, RecordTypeEnum.MIDI_UNLIMITED),
        )

        def switch_monitoring() -> None:
            assert hasattr(
                Song.current_track(), "monitoring_state"
            ), "current track cannot be monitored"
            Song.current_track().monitoring_state.switch()  # noqa

        # MONitor encoder
        self.add_encoder(
            identifier=5,
            name="monitor",
            filter_active_tracks=True,
            on_press=switch_monitoring,
        )
