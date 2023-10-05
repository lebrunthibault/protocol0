import os
import shutil
from os.path import basename
from time import sleep

from p0_backend.api.client.p0_script_api_client import p0_script_client
from p0_backend.lib.ableton.interface.browser import (
    toggle_browser,
    is_browser_visible,
    click_browser_tracks,
)
from p0_backend.lib.ableton.interface.coords import CoordsEnum
from p0_backend.lib.ableton.interface.track import get_focused_track_coords
from p0_backend.lib.ableton.ableton_set.ableton_set import AbletonSet
from p0_backend.lib.decorators import retry
from p0_backend.lib.errors.Protocol0Error import Protocol0Error
from p0_backend.lib.explorer import open_explorer
from p0_backend.lib.keys import send_keys
from p0_backend.lib.mouse.mouse import drag_to, keep_mouse_position, move_to
from protocol0.application.command.EmitBackendEventCommand import (
    EmitBackendEventCommand,
)


@retry(90, 0)  # 9 seconds max
def _wait_for_track_save(ableton_set: AbletonSet):
    sleep(0.1)
    assert ableton_set.is_current_track_saved, "Track not yet saved"


@retry(5, 0.1)
def _close_browser():
    toggle_browser()
    assert not is_browser_visible()


@keep_mouse_position
def save_track_to_sub_tracks(ableton_set: AbletonSet, check_for_duplicate=False):
    assert len(AbletonSet.all_tracks_folder()) < 8, "Too many set tracks, drag cannot be made"
    if ableton_set.saved_temp_track is not None:
        os.unlink(ableton_set.saved_temp_track)

    if check_for_duplicate:
        duplicate = next(
            filter(
                lambda t: basename(t).split(".")[0] == ableton_set.current_state.selected_track.name, ableton_set.saved_tracks  # type: ignore
            ),
            None,
        )
        if duplicate is not None:
            open_explorer(duplicate)  # type: ignore[arg-type]
            raise Protocol0Error("Duplicate saved track")

    click_browser_tracks()

    # drag the track to the tracks folder
    move_to(get_focused_track_coords())
    drag_to(CoordsEnum.BROWSER_FREE_TRACK_SPOT.value, duration=0.3)  # drag to a free spot

    _wait_for_track_save(ableton_set)

    shutil.move(str(ableton_set.saved_temp_track), f"{ableton_set.path_info.tracks_folder}/{ableton_set.current_state.current_track.name}.als")

    sleep(0.1)
    send_keys("{ESC}")  # close the name prompt
    _close_browser()

    p0_script_client().dispatch(EmitBackendEventCommand("track_saved"))
