from functools import partial

from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface
from protocol0.domain.lom.set.MixingService import MixingService
from protocol0.domain.lom.song.components.TempoComponent import TempoComponent

# noinspection SpellCheckingInspection
from protocol0.domain.track_recorder.RecordService import RecordService


class ActionGroupMain(ActionGroupInterface):
    CHANNEL = 4

    def configure(self) -> None:
        # TAP tempo encoder
        self.add_encoder(
            identifier=1,
            name="tap tempo",
            on_press=self._container.get(TempoComponent).tap,
            on_scroll=self._container.get(TempoComponent).scroll,
        )

        # RESAmple encoder
        self.add_encoder(
            identifier=5,
            name="Resample",
            on_press=self._container.get(RecordService).resample_selected_track,
            on_long_press=partial(
                self._container.get(RecordService).resample_selected_track, record_audio=True
            ),
        )

        self.add_encoder(identifier=13, name="test", on_press=self.action_test)

        # ADPTr Metric AB stereo mode
        self.add_encoder(
            identifier=16,
            name="test",
            on_press=partial(self._container.get(MixingService).toggle_adptr_stereo_mode, "mono"),
            on_long_press=partial(
                self._container.get(MixingService).toggle_adptr_stereo_mode, "sides"
            ),
        )

    def action_test(self) -> None:
        pass
