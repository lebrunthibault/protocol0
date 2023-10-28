from p0_backend.api.client.p0_script_api_client import p0_script_client
from p0_backend.settings import DOWN_BBOX
from p0_backend.lib.ableton.interface.track import get_focused_track_coords
from p0_backend.lib.ableton.ableton_set.ableton_set import AbletonSet
from p0_backend.lib.explorer import drag_file_to
from p0_backend.lib.mouse.mouse import keep_mouse_position
from protocol0.application.command.EmitBackendEventCommand import (
    EmitBackendEventCommand,
)


@keep_mouse_position
def drag_matching_track(ableton_set: AbletonSet):
    track_path = (
        f"{ableton_set.path_info.tracks_folder}\\{ableton_set.current_state.current_track.name}.als"
    )
    drag_file_to(
        track_path,
        get_focused_track_coords(),
        bbox=DOWN_BBOX,
        drag_duration=0.5,
        close_window=False,
    )
    p0_script_client().dispatch(EmitBackendEventCommand("matching_track_loaded"))
