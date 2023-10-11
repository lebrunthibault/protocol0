from fastapi import APIRouter

from p0_backend.api.client.p0_script_api_client import p0_script_client
from p0_backend.lib.ableton.interface.clip import set_clip_file_path, crop_clip
from protocol0.application.command.ColorClipWithAutomationCommand import (
    ColorClipWithAutomationCommand,
)
from protocol0.application.command.MatchClipColorCommand import MatchClipColorCommand
from protocol0.application.command.MoveClipLoopCommand import MoveClipLoopCommand
from protocol0.application.command.SelectClipCommand import SelectClipCommand
from protocol0.application.command.SetClipLoopLengthCommand import SetClipLoopLengthCommand
from protocol0.application.command.ToggleClipCommand import ToggleClipCommand
from protocol0.application.command.ToggleNotesCommand import ToggleNotesCommand

router = APIRouter()


@router.get("/crop")
def _crop_clip():
    crop_clip()


@router.get("/set_file_path")
def _set_clip_file_path(file_path: str):
    set_clip_file_path(file_path)


@router.get("/select")
async def select_clip(track_name: str):
    p0_script_client().dispatch(SelectClipCommand(track_name))


@router.get("/toggle")
async def toggle_clip(track_name: str):
    p0_script_client().dispatch(ToggleClipCommand(track_name))


@router.get("/toggle_notes")
async def _toggle_clip_notes():
    p0_script_client().dispatch(ToggleNotesCommand())


@router.get("/match_colors")
async def _match_clip_colors():
    p0_script_client().dispatch(MatchClipColorCommand())


@router.get("/color_with_automation")
async def _color_clip_with_automation():
    p0_script_client().dispatch(ColorClipWithAutomationCommand())


@router.get("/move_loop")
async def move_loop(forward: bool = True):
    p0_script_client().dispatch(MoveClipLoopCommand(forward=forward))


@router.get("/set_loop_length")
async def set_loop_length(bar_length: int):
    p0_script_client().dispatch(SetClipLoopLengthCommand(bar_length=bar_length))
