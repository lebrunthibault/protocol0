from functools import partial

from _Framework.Util import find_if

from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface
from protocol0.domain.live_set.LiveSetInstruments import (
    move_clip_loop,
    change_clip_loop,
    sync_markers,
)

# noinspection SpellCheckingInspection
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.track.simple_track.audio.master.MasterTrack import MasterTrack
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.shared.Song import Song


class ActionGroupLive4(ActionGroupInterface):
    CHANNEL = 4

    def configure(self) -> None:
        self.add_encoder(
            identifier=4, name="move clip loop", on_scroll=move_clip_loop, on_press=sync_markers
        )
        self.add_encoder(identifier=5, name="clip loop 1", on_press=partial(change_clip_loop, 1))
        self.add_encoder(identifier=6, name="clip loop 2", on_press=partial(change_clip_loop, 2))
        self.add_encoder(identifier=7, name="clip loop 4", on_press=partial(change_clip_loop, 4))
        self.add_encoder(identifier=8, name="clip loop 8", on_press=partial(change_clip_loop, 8))

        # self.add_encoder(
        #     identifier=1,
        #     name="Resample",
        #     on_press=self._container.get(RecordService).resample_selected_track,
        # )

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

        # self.add_encoder(
        #     identifier=13,
        #     name="Splice Bridge",
        #     on_press=toggle_splice_track,
        #     on_long_press=create_splice_track,
        #     on_scroll=scroll_splice_track_volume,
        # )

        def scroll_selected_track_volume(go_next: bool) -> None:
            assert not isinstance(Song.selected_track(), MasterTrack), "Cannot scroll master volume"
            Song.selected_track().scroll_volume(go_next)

        # self.add_encoder(
        #     identifier=15,
        #     name="track volume",
        #     on_scroll=scroll_selected_track_volume,
        # )

        def scroll_selected_parameter(go_next: bool) -> None:
            assert Song.selected_parameter(), "No selected parameter"
            Song.selected_parameter().scroll(go_next)

        #
        # self.add_encoder(
        #     identifier=16, name="scroll_selected_parameter", on_scroll=scroll_selected_parameter
        # )
