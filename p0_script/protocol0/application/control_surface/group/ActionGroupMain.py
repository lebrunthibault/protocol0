from functools import partial

from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface

# noinspection SpellCheckingInspection
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.track.simple_track.audio.master.MasterTrack import MasterTrack
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.track_recorder.RecordService import RecordService
from protocol0.domain.track_recorder.RecordTypeEnum import RecordTypeEnum
from protocol0.shared.Song import Song


class ActionGroupMain(ActionGroupInterface):
    CHANNEL = 4

    def configure(self) -> None:
        self.add_encoder(
            identifier=1,
            name="Resample",
            on_press=self._container.get(RecordService).resample_selected_track,
        )

        self.add_encoder(identifier=4, name="test", on_press=self.action_test)

        def activate_adptr_filter(filter_type: str) -> None:
            Song.master_track().activate_adptr_filter(filter_type)

        self.add_encoder(
            identifier=9, name="ref bass", on_press=partial(activate_adptr_filter, "bass")
        )
        self.add_encoder(
            identifier=10, name="ref low_mid", on_press=partial(activate_adptr_filter, "low_mid")
        )
        self.add_encoder(
            identifier=11, name="ref mid", on_press=partial(activate_adptr_filter, "mid")
        )
        self.add_encoder(
            identifier=12, name="ref high", on_press=partial(activate_adptr_filter, "high")
        )

        def toggle_splice_track() -> None:
            if Song.splice_track():
                Song.splice_track().toggle()
            else:
                Backend.client().load_device(DeviceEnum.SPLICE_BRIDGE.name)

        def create_splice_track() -> None:
            Backend.client().load_device(DeviceEnum.SPLICE_BRIDGE.name)

        def scroll_splice_track_volume(go_next: bool) -> None:
            if Song.splice_track():
                Song.splice_track().devices.mixer_device.volume.scroll(go_next)

        self.add_encoder(
            identifier=13,
            name="Splice Bridge",
            on_press=toggle_splice_track,
            on_long_press=create_splice_track,
            on_scroll=scroll_splice_track_volume,
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

        self.add_encoder(
            identifier=16, name="scroll_selected_parameter", on_scroll=scroll_selected_parameter
        )

    def action_test(self) -> None:
        first_armed_track = next(iter(Song.armed_tracks()), None)
        assert first_armed_track, "No track armed"
        self._container.get(RecordService).record_tracks(Song.armed_tracks(), RecordTypeEnum.MIDI)
        from protocol0.shared.logging.Logger import Logger

        Logger.dev("toto")
