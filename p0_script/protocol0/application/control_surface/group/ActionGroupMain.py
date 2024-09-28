from functools import partial

from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface

# noinspection SpellCheckingInspection
from protocol0.domain.lom.track.simple_track.audio.master.MasterTrack import MasterTrack
from protocol0.domain.track_recorder.RecordService import RecordService
from protocol0.shared.Song import Song


class ActionGroupMain(ActionGroupInterface):
    CHANNEL = 4

    def configure(self) -> None:
        self.add_encoder(
            identifier=1,
            name="Resample",
            on_press=partial(
                self._container.get(RecordService).resample_selected_track, record_audio=True
            ),
            on_long_press=self._container.get(RecordService).resample_selected_track,
        )

        self.add_encoder(identifier=4, name="test", on_press=self.action_test)

        def toggle_splice_track() -> None:
            if Song.splice_track():
                Song.splice_track().toggle()

        def solo_splice_track() -> None:
            if Song.splice_track():
                Song.splice_track().solo_toggle()

        def scroll_splice_track(go_next: bool) -> None:
            if Song.splice_track():
                Song.splice_track().devices.mixer_device.volume.scroll(go_next)

        self.add_encoder(
            identifier=13,
            name="Splice Bridge",
            on_press=toggle_splice_track,
            on_long_press=solo_splice_track,
            on_scroll=scroll_splice_track,
        )

        def scroll_selected_track_volume(go_next: bool) -> None:
            assert not isinstance(Song.selected_track(), MasterTrack), "Cannot scroll master volume"
            Song.selected_track().scroll_volume(go_next)

        self.add_encoder(
            identifier=15,
            name="track volume",
            on_scroll=scroll_selected_track_volume,
        )

        def scroll_selected_parameter(go_next: bool) -> None:
            assert Song.selected_parameter(), "No selected parameter"
            Song.selected_parameter().scroll(go_next)

        self.add_encoder(identifier=16, name="test", on_scroll=scroll_selected_parameter)

    def action_test(self) -> None:
        pass
