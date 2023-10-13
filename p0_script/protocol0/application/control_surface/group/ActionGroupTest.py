from functools import partial

from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface
from protocol0.domain.audit.AudioLatencyAnalyzerService import AudioLatencyAnalyzerService
from protocol0.domain.lom.song.components.PlaybackComponent import PlaybackComponent
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger


class ActionGroupTest(ActionGroupInterface):
    CHANNEL = 13

    def configure(self) -> None:
        # TEST encoder
        self.add_encoder(
            identifier=1, name="test", on_press=self.action_test, on_scroll=self.action_test_scroll
        )

        # PROFiling encoder
        self.add_encoder(
            identifier=2,
            name="start set launch time profiling",
            on_press=Backend.client().start_set_profiling,
        )

        # CLR encoder
        self.add_encoder(identifier=3, name="clear logs", on_press=Logger.clear)

        # USAMo encoder
        self.add_encoder(
            identifier=13,
            name="check usamo latency",
            on_press=lambda: partial(
                self._container.get(AudioLatencyAnalyzerService).test_audio_latency,
                Song.current_external_synth_track(),
            ),
        )

    def action_test(self) -> None:
        self._container.get(PlaybackComponent).stop_playing()

    def action_test_scroll(self, go_next: bool) -> None:
        Song.selected_track().instrument.preset_list.scroll(go_next)
