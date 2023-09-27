from itertools import chain
from time import sleep
from typing import Optional, List, Dict

from fastapi import APIRouter

from p0_backend.api.client.p0_script_api_client import p0_script_client
from p0_backend.api.http_server.ws import ws_manager
from p0_backend.celery.celery import notification_window, create_app
from p0_backend.lib.ableton.ableton import (
    reload_ableton,
    clear_arrangement,
    save_set,
    hide_plugins,
    show_plugins,
    open_set,
)
from p0_backend.lib.ableton.ableton import (
    save_set_as_template,
    open_set_by_type,
)
from p0_backend.lib.ableton.analyze_clip_jitter import analyze_test_audio_clip_jitter
from p0_backend.lib.ableton.automation import edit_automation_value
from p0_backend.lib.ableton.automation import set_envelope_loop_length
from p0_backend.lib.ableton.external_synth_track import (
    activate_rev2_editor,
    post_activate_rev2_editor,
)
from p0_backend.lib.ableton.interface.browser import preload_sample_category
from p0_backend.lib.ableton.interface.clip import set_clip_file_path, crop_clip
from p0_backend.lib.ableton.interface.sample import load_sample_in_simpler
from p0_backend.lib.ableton.interface.toggle_ableton_button import toggle_ableton_button
from p0_backend.lib.ableton.interface.track import click_focused_track
from p0_backend.lib.ableton.interface.track import flatten_track, load_instrument_track
from p0_backend.lib.ableton.matching_track.load_matching_track import drag_matching_track
from p0_backend.lib.ableton.matching_track.save_track import save_track_to_sub_tracks
from p0_backend.lib.ableton.set_profiling.ableton_set_profiler import AbletonSetProfiler
from p0_backend.lib.ableton_set import AbletonSet, AbletonSetLight
from p0_backend.lib.ableton_set import AbletonSetManager, show_saved_tracks, delete_saved_track
from p0_backend.lib.enum.notification_enum import NotificationEnum
from p0_backend.lib.errors.Protocol0Error import Protocol0Error
from p0_backend.lib.explorer import close_samples_windows, close_explorer_window, open_explorer
from p0_backend.lib.keys import send_keys
from p0_backend.lib.mouse.mouse import click, click_vertical_zone, move_to
from p0_backend.lib.process import execute_powershell_command
from p0_backend.lib.scene_stats import SceneStats
from p0_backend.lib.server_state import ServerState, list_sets
from p0_backend.lib.window.find_window import find_window_handle_by_enum
from p0_backend.lib.window.window import focus_window
from p0_backend.settings import Settings
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
from .script_actions.router import router as script_actions_router

router = APIRouter()

settings = Settings()

router.include_router(script_actions_router, prefix="/actions")


@router.get("/")
def home() -> str:
    return "ok"


@router.get("/ping")
def ping():
    AbletonSetProfiler.end_measurement()


@router.get("/search")
def search(text: str):
    send_keys("^f")
    sleep(0.1)
    send_keys(text)


@router.get("/show_sample_category")
def show_sample_category(category: str):
    preload_sample_category(category)


@router.get("/reload_ableton")
async def _reload_ableton():
    reload_ableton()


@router.get("/flatten_track")
def _flatten_track():
    flatten_track()


@router.get("/crop_clip")
def _crop_clip():
    crop_clip()


@router.get("/move_to")
def _move_to(x: int, y: int):
    move_to((x, y))


@router.get("/click")
def _click(x: int, y: int):
    click((x, y))


@router.get("/click_vertical_zone")
def _click_vertical_zone(x: int, y: int):
    click_vertical_zone((x, y))


@router.get("/select_and_copy")
def select_and_copy():
    send_keys("^a")
    send_keys("^c")


@router.get("/select_and_paste")
def select_and_paste():
    send_keys("^a")
    send_keys("^v")


@router.get("/analyze_test_audio_clip_jitter")
def _analyze_test_audio_clip_jitter(clip_path: str):
    analyze_test_audio_clip_jitter(clip_path=clip_path)


@router.get("/show_plugins")
def _show_plugins():
    show_plugins()


@router.get("/show_hide_plugins")
def show_hide_plugins():
    send_keys("^%p")


@router.get("/hide_plugins")
def _hide_plugins():
    hide_plugins()


@router.get("/save_set")
def _save_set():
    save_set()


@router.get("/clear_arrangement")
def _clear_arrangement():
    clear_arrangement()


@router.get("/toggle_ableton_button")
def _toggle_ableton_button(x: int, y: int, activate: bool = False):
    toggle_ableton_button((x, y), activate=activate)


@router.get("/load_instrument_track")
def _load_instrument_track(instrument_name: str):
    load_instrument_track(instrument_name)


@router.get("/load_sample_in_simpler")
def _load_sample_in_simpler(sample_path: str):
    load_sample_in_simpler(sample_path)


@router.get("/set_clip_file_path")
def _set_clip_file_path(file_path: str):
    set_clip_file_path(file_path)


@router.get("/set_envelope_loop_length")
def _set_envelope_loop_length(length: int):
    set_envelope_loop_length(length)


@router.get("/activate_rev2_editor")
def _activate_rev2_editor():
    activate_rev2_editor()


@router.get("/post_activate_rev2_editor")
def _post_activate_rev2_editor():
    post_activate_rev2_editor()


@router.get("/start_set_profiling")
def start_set_profiling():
    AbletonSetProfiler.start_set_profiling()


@router.get("/start_profiling_single_measurement")
def start_profiling_single_measurement():
    AbletonSetProfiler.start_profiling_single_measurement()


@router.get("/close_samples_windows")
def _close_samples_windows():
    close_samples_windows()


@router.get("/close_explorer_window")
def _close_explorer_window(title: str):
    close_explorer_window(title)


@router.get("/show_info")
def show_info(message: str, body: str = ""):
    create_app()
    notification_window.delay(message, NotificationEnum.INFO, body=body)


@router.get("/show_success")
def show_success(message: str):
    create_app()
    notification_window.delay(message, NotificationEnum.SUCCESS)


@router.get("/show_warning")
def show_warning(message: str):
    create_app()
    notification_window.delay(message, NotificationEnum.WARNING)


@router.get("/show_error")
def show_error(message: str):
    create_app()
    notification_window.delay(message, NotificationEnum.ERROR)


@router.get("/reload_script")
async def _reload_script():
    p0_script_client().dispatch(ReloadScriptCommand())


@router.get("/server_state")
async def server_state() -> ServerState:
    return ServerState.create()


@router.get("/sets")
async def sets() -> Dict[str, List[AbletonSetLight]]:
    return list_sets()


@router.get("/set")
async def get_set(path: str) -> AbletonSetLight:
    path = path.replace("\\\\", "\\")

    ableton_sets = list(chain.from_iterable(list_sets().values()))

    return next(s for s in ableton_sets if s.path == path)


@router.post("/set")
async def post_set(ableton_set: AbletonSet):
    """Forwarded from midi server"""
    from loguru import logger

    logger.success(ableton_set)
    await AbletonSetManager.register(ableton_set)


@router.put("/set", include_in_schema=False)
async def update_set(title: str, path: Optional[str] = None):
    AbletonSetManager.update_set(title, path)


@router.get("/close_set")
async def close_set(set_id: str):
    await AbletonSetManager.remove(set_id)
    await ws_manager.broadcast_server_state()


@router.post("/scene_stats")
async def post_scene_stats(scene_stats: SceneStats):
    from loguru import logger

    logger.success(scene_stats.dict())

    with open(AbletonSetManager.active().metadata_path, "w") as f:
        f.write(scene_stats.json())


@router.get("/save_set_as_template")
async def _save_set_as_template():
    save_set_as_template()


@router.get("/tail_logs")
async def tail_logs():
    if find_window_handle_by_enum(settings.log_window_title):
        focus_window(settings.log_window_title)
        return

    execute_powershell_command("poetry run logs")


@router.get("/tail_logs_raw")
async def tail_logs_raw():
    execute_powershell_command("poetry run logs-raw")


@router.get("/open_in_explorer")
async def open_in_explorer(path: str):
    open_explorer(path)


@router.get("/set/open")
async def _open_set(path: str):
    open_set(path)


@router.get("/set/open_by_type")
async def _open_set_by_type(name: str):
    open_set_by_type(name)


@router.get("/play_pause")
async def play_pause():
    p0_script_client().dispatch(PlayPauseSongCommand())


@router.get("/load_device")
async def load_device(name: str):
    p0_script_client().dispatch(LoadDeviceCommand(name))


@router.get("/select_or_load_device")
async def select_or_load_device(name: str):
    p0_script_client().dispatch(SelectOrLoadDeviceCommand(name))


@router.get("/load_drum_rack")
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


@router.get("/delete_saved_track")
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


@router.get("/fire_scene_to_last_position")
async def fire_scene_to_last_position():
    p0_script_client().dispatch(FireSceneToPositionCommand(None))


@router.get("/fire_scene_to_position")
async def fire_scene_to_position(bar_length: int = 0):
    from loguru import logger

    logger.info(f"fire_scene_to_position: {bar_length}")
    p0_script_client().dispatch(FireSceneToPositionCommand(bar_length))


@router.get("/fire_selected_scene")
async def fire_selected_scene():
    p0_script_client().dispatch(FireSelectedSceneCommand())


@router.get("/record_unlimited")
async def record_unlimited():
    p0_script_client().dispatch(RecordUnlimitedCommand())


@router.get("/scroll_scenes")
async def scroll_scenes(direction: str):
    p0_script_client().dispatch(ScrollScenesCommand(go_next=direction == "next"))


@router.get("/scroll_scene_position")
async def scroll_scene_position(direction: str):
    p0_script_client().dispatch(ScrollScenePositionCommand(go_next=direction == "next"))


@router.get("/scroll_scene_position_fine")
async def scroll_scene_position_fine(direction: str):
    p0_script_client().dispatch(
        ScrollScenePositionCommand(go_next=direction == "next", use_fine_scrolling=True)
    )


@router.get("/scroll_scene_tracks")
async def scroll_scene_tracks(direction: str):
    p0_script_client().dispatch(ScrollSceneTracksCommand(go_next=direction == "next"))


@router.get("/scroll_track_volume")
async def scroll_track_volume(direction: str):
    p0_script_client().dispatch(ScrollTrackVolumeCommand(go_next=direction == "next"))


@router.get("/toggle_reference")
async def toggle_reference():
    p0_script_client().dispatch(ToggleReferenceTrackCommand())


@router.get("/show_instrument")
async def show_instrument():
    p0_script_client().dispatch(ShowInstrumentCommand())


@router.get("/show_automation")
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
