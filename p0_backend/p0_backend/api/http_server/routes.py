from typing import Optional

from fastapi import APIRouter
from protocol0.application.command.BounceTrackToAudioCommand import BounceTrackToAudioCommand
from protocol0.application.command.CheckAudioExportValidCommand import CheckAudioExportValidCommand
from protocol0.application.command.DrumRackToSimplerCommand import DrumRackToSimplerCommand
from protocol0.application.command.FireSceneToPositionCommand import FireSceneToPositionCommand
from protocol0.application.command.FireSelectedSceneCommand import FireSelectedSceneCommand
from protocol0.application.command.GoToGroupTrackCommand import GoToGroupTrackCommand
from protocol0.application.command.LoadDeviceCommand import LoadDeviceCommand
from protocol0.application.command.LoadDrumRackCommand import LoadDrumRackCommand
from protocol0.application.command.LoadMatchingTrackCommand import LoadMatchingTrackCommand
from protocol0.application.command.LoadMinitaurCommand import LoadMinitaurCommand
from protocol0.application.command.LoadRev2Command import LoadRev2Command
from protocol0.application.command.MidiNoteCommand import MidiNoteCommand
from protocol0.application.command.PlayPauseSongCommand import PlayPauseSongCommand
from protocol0.application.command.RecordUnlimitedCommand import RecordUnlimitedCommand
from protocol0.application.command.ReloadScriptCommand import ReloadScriptCommand
from protocol0.application.command.ScrollScenePositionCommand import ScrollScenePositionCommand
from protocol0.application.command.ScrollSceneTracksCommand import ScrollSceneTracksCommand
from protocol0.application.command.ScrollScenesCommand import ScrollScenesCommand
from protocol0.application.command.ScrollTrackVolumeCommand import ScrollTrackVolumeCommand
from protocol0.application.command.SelectOrLoadDeviceCommand import SelectOrLoadDeviceCommand
from protocol0.application.command.ShowAutomationCommand import ShowAutomationCommand
from protocol0.application.command.ShowInstrumentCommand import ShowInstrumentCommand
from protocol0.application.command.ToggleArmCommand import ToggleArmCommand
from protocol0.application.command.ToggleNotesCommand import ToggleNotesCommand
from protocol0.application.command.ToggleReferenceTrackCommand import ToggleReferenceTrackCommand
from protocol0.application.command.ToggleSceneLoopCommand import ToggleSceneLoopCommand

from p0_backend.api.client.p0_script_api_client import p0_script_client
from p0_backend.api.http_server.ws import ws_manager
from p0_backend.api.settings import Settings
from p0_backend.lib.ableton.ableton import (
    reload_ableton,
    save_set_as_template,
    open_set_by_type,
)
from p0_backend.lib.ableton.automation import edit_automation_value
from p0_backend.lib.ableton.interface.track import click_focused_track
from p0_backend.lib.ableton.matching_track.load_matching_track import drag_matching_track
from p0_backend.lib.ableton.matching_track.save_track import save_track_to_sub_tracks
from p0_backend.lib.ableton_set import AbletonSetManager, AbletonSet, show_saved_tracks, delete_saved_track
from p0_backend.lib.errors.Protocol0Error import Protocol0Error
from p0_backend.lib.process import execute_python_script_in_new_window
from p0_backend.lib.server_state import ServerState
from p0_backend.lib.window.find_window import find_window_handle_by_enum
from p0_backend.lib.window.window import focus_window
from .script_actions.router import router as script_actions_router

router = APIRouter()

settings = Settings()

router.include_router(script_actions_router, prefix="/actions")


@router.get("/reload_ableton")
async def _reload_ableton():
    reload_ableton()


@router.get("/test")
async def test():
    p0_script_client().dispatch(MidiNoteCommand(13, 1))  # test
    # p0_script_client().dispatch(MidiNoteCommand(9, 4))  # bounce set


@router.get("/reload_script")
async def _reload_script():
    p0_script_client().dispatch(ReloadScriptCommand())


@router.get("/server_state")
async def server_state() -> ServerState:
    return ServerState.create()


@router.post("/set")
async def post_set(ableton_set: AbletonSet):
    """Forwarded from midi server"""
    await AbletonSetManager.register(ableton_set)


@router.put("/set")
async def update_set(title: str, path: Optional[str] = None):
    AbletonSetManager.update_set(title, path)


@router.delete("/set/{set_id}")
async def delete_set(set_id: str):
    await AbletonSetManager.remove(set_id)
    await ws_manager.broadcast_server_state()


@router.get("/save_set_as_template")
async def _save_set_as_template():
    save_set_as_template()


@router.get("/tail_logs")
async def tail_logs():
    if find_window_handle_by_enum(settings.log_window_title):
        focus_window(settings.log_window_title)
        return

    execute_python_script_in_new_window(
        f"{settings.project_directory}/scripts/tail_protocol0_logs.py", min=False
    )


@router.get("/tail_logs_raw")
async def tail_logs_raw():
    execute_python_script_in_new_window(
        f"{settings.project_directory}/scripts/tail_protocol0_logs.py", "--raw"
    )


@router.get("/set/{name}/open")
async def _open_set(name: str):
    open_set_by_type(name)


@router.get("/play_pause")
async def play_pause():
    p0_script_client().dispatch(PlayPauseSongCommand())


@router.get("/load_device/{name}")
async def load_device(name: str):
    p0_script_client().dispatch(LoadDeviceCommand(name))


@router.get("/select_or_load_device/{name}")
async def select_or_load_device(name: str):
    p0_script_client().dispatch(SelectOrLoadDeviceCommand(name))


@router.get("/load_drum_rack/{category}/{subcategory}")
async def load_drum_rack(category: str, subcategory: str):
    p0_script_client().dispatch(LoadDrumRackCommand(category, subcategory))


@router.get("/load_rev2")
async def load_rev2():
    p0_script_client().dispatch(LoadRev2Command())


@router.get("/load_minitaur")
async def load_minitaur():
    p0_script_client().dispatch(LoadMinitaurCommand())


@router.get("/bounce_track_to_audio")
async def _bounce_track_to_audio():
    p0_script_client().dispatch(BounceTrackToAudioCommand())


@router.get("/click_focused_track")
async def _click_focused_track():
    click_focused_track()


@router.get("/save_track_to_sub_tracks")
async def _save_track_to_sub_tracks():
    save_track_to_sub_tracks(AbletonSetManager.active())


@router.get("/load_matching_track")
async def load_matching_track():
    p0_script_client().dispatch(LoadMatchingTrackCommand())


@router.get("/drag_matching_track")
async def _drag_matching_track():
    drag_matching_track(AbletonSetManager.active())


@router.get("/show_saved_tracks")
async def _show_saved_tracks():
    show_saved_tracks()


@router.get("/delete_saved_track/{track_name}")
async def _delete_saved_track(track_name: str):
    delete_saved_track(track_name)


@router.get("/drum_rack_to_simpler")
async def drum_rack_to_simpler():
    p0_script_client().dispatch(DrumRackToSimplerCommand())


@router.get("/arm")
async def arm():
    p0_script_client().dispatch(ToggleArmCommand())


@router.get("/toggle_scene_loop")
async def toggle_scene_loop():
    p0_script_client().dispatch(ToggleSceneLoopCommand())


@router.get("/fire_scene_to_position/{bar_length}")
@router.get("/fire_scene_to_position")
async def fire_scene_to_position(bar_length: Optional[int] = None):
    p0_script_client().dispatch(FireSceneToPositionCommand(bar_length))


@router.get("/fire_selected_scene")
async def fire_selected_scene():
    p0_script_client().dispatch(FireSelectedSceneCommand())


@router.get("/record_unlimited")
async def record_unlimited():
    p0_script_client().dispatch(RecordUnlimitedCommand())


@router.get("/scroll_scenes/{direction}")
async def scroll_scenes(direction: str):
    p0_script_client().dispatch(ScrollScenesCommand(go_next=direction == "next"))


@router.get("/scroll_scene_position/{direction}")
async def scroll_scene_position(direction: str):
    p0_script_client().dispatch(ScrollScenePositionCommand(go_next=direction == "next"))


@router.get("/scroll_scene_position_fine/{direction}")
async def scroll_scene_position_fine(direction: str):
    p0_script_client().dispatch(
        ScrollScenePositionCommand(go_next=direction == "next", use_fine_scrolling=True)
    )


@router.get("/scroll_scene_tracks/{direction}")
async def scroll_scene_tracks(direction: str):
    p0_script_client().dispatch(ScrollSceneTracksCommand(go_next=direction == "next"))


@router.get("/scroll_track_volume/{direction}")
async def scroll_track_volume(direction: str):
    p0_script_client().dispatch(ScrollTrackVolumeCommand(go_next=direction == "next"))


@router.get("/toggle_reference")
async def toggle_reference():
    p0_script_client().dispatch(ToggleReferenceTrackCommand())


@router.get("/show_instrument")
async def show_instrument():
    p0_script_client().dispatch(ShowInstrumentCommand())


@router.get("/show_automation/{direction}")
async def show_automation(direction: str):
    p0_script_client().dispatch(ShowAutomationCommand(go_next=direction == "next"))


@router.get("/toggle_clip_notes")
async def _toggle_clip_notes():
    p0_script_client().dispatch(ToggleNotesCommand())


@router.get("/edit_automation_value")
async def _edit_automation_value():
    try:
        active_set = AbletonSetManager.active()
    except Protocol0Error:
        active_set = None

    if active_set is not None:
        assert active_set.selected_track.type in (
            "SimpleAudioTrack",
            "SimpleAudioExtTrack",
            "SimpleMidiTrack",
            "SimpleMidiExtTrack",
        ), "cannot edit automation"

    edit_automation_value()


@router.get("/go_to_group_track")
async def _go_to_group_track():
    p0_script_client().dispatch(GoToGroupTrackCommand())


@router.get("/check_audio_export_valid")
async def check_audio_export_valid():
    p0_script_client().dispatch(CheckAudioExportValidCommand())
