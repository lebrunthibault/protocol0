from fastapi import APIRouter

from p0_backend.api.client.p0_script_api_client import p0_script_client
from p0_backend.lib.ableton.ableton_set.ableton_set_manager import (
    AbletonSetManager,
)
from p0_backend.lib.ableton.automation import edit_automation_value
from p0_backend.lib.ableton.interface.clip import crop_clip
from p0_backend.lib.errors.Protocol0Error import Protocol0Error
from protocol0.application.command.LoopSelectedClipCommand import LoopSelectedClipCommand
from protocol0.application.command.MoveClipLoopCommand import MoveClipLoopCommand
from protocol0.application.command.CleanLoopCommand import (
    CleanLoopCommand,
)
from protocol0.application.command.RemoveMutedNotesCommand import (
    RemoveMutedNotesCommand,
)
from protocol0.application.command.SelectClipCommand import SelectClipCommand
from protocol0.application.command.SetClipLoopLengthCommand import SetClipLoopLengthCommand
from protocol0.application.command.ToggleClipCommand import ToggleClipCommand
from protocol0.application.command.ToggleNotesCommand import ToggleNotesCommand

router = APIRouter()


@router.get("/crop")
def _crop_clip():
    crop_clip()


@router.get("/select")
async def select_clip(track_name: str):
    p0_script_client().dispatch(SelectClipCommand(track_name))


@router.get("/toggle")
async def toggle_clip(track_name: str):
    p0_script_client().dispatch(ToggleClipCommand(track_name))


@router.get("/toggle_notes")
async def _toggle_clip_notes():
    p0_script_client().dispatch(ToggleNotesCommand())


@router.get("/loop_selected")
async def loop_selected():
    p0_script_client().dispatch(LoopSelectedClipCommand())


@router.get("/move_loop")
async def move_loop(forward: bool = True, bar: bool = False):
    p0_script_client().dispatch(MoveClipLoopCommand(forward=forward, bar=bar))


@router.get("/set_loop_length")
async def set_loop_length(bar_length: int):
    p0_script_client().dispatch(SetClipLoopLengthCommand(bar_length=bar_length))


@router.get("/edit_automation_value")
async def _edit_automation_value():
    try:
        active_set = AbletonSetManager.active()
    except Protocol0Error:
        active_set = None

    if active_set is not None:
        assert active_set.current_state.selected_track.type in (
            "SimpleAudioTrack",
            "SimpleMidiTrack",
        ), "cannot edit automation"

    edit_automation_value()


@router.get("/clean_arrangement_loop")
async def clean_arrangement_loop():
    p0_script_client().dispatch(CleanLoopCommand())


@router.get("/clear_muted_notes")
async def clear_muted_notes():
    p0_script_client().dispatch(RemoveMutedNotesCommand())
