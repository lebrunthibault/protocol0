from functools import partial

from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface
from protocol0.domain.lom.set.MixingService import MixingService
from protocol0.domain.lom.song.components.TempoComponent import TempoComponent

# noinspection SpellCheckingInspection
from protocol0.domain.track_recorder.RecordService import RecordService
from protocol0.shared.Song import Song
from protocol0.shared.sequence.Sequence import Sequence


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

        def toggle_splice_track() -> None:
            if Song.splice_track():
                Song.splice_track().toggle()

        def scroll_splice_track(go_next: bool) -> None:
            if Song.splice_track():
                Song.splice_track().devices.mixer_device.volume.scroll(go_next)

        # SPLIce bridge encoder
        self.add_encoder(
            identifier=4,
            name="Splice Bridge",
            on_press=toggle_splice_track,
            on_scroll=scroll_splice_track,
        )

        # RESAmple encoder
        self.add_encoder(
            identifier=5,
            name="Resample",
            on_press=partial(
                self._container.get(RecordService).resample_selected_track, record_audio=True
            ),
            on_long_press=self._container.get(RecordService).resample_selected_track,
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
        seq = Sequence()

        for track in Song.simple_tracks():
            if track.is_foldable or track.has_midi_output:
                continue

            seq.add(track.add_to_selection)

        seq.done()
