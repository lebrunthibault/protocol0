from fastapi import APIRouter

from p0_backend.api.client.p0_script_api_client import p0_script_client
from protocol0.application.command.DuplicateSceneCommand import DuplicateSceneCommand
from protocol0.application.command.FireSceneToPositionCommand import FireSceneToPositionCommand
from protocol0.application.command.FireSelectedSceneCommand import FireSelectedSceneCommand
from protocol0.application.command.ScrollScenePositionCommand import ScrollScenePositionCommand
from protocol0.application.command.ScrollSceneTracksCommand import ScrollSceneTracksCommand
from protocol0.application.command.ScrollScenesCommand import ScrollScenesCommand
from protocol0.application.command.ToggleSceneLoopCommand import ToggleSceneLoopCommand


router = APIRouter()

@router.get("/toggle_loop")
async def toggle_scene_loop():
    p0_script_client().dispatch(ToggleSceneLoopCommand())


@router.get("/fire_to_last_position")
async def fire_scene_to_last_position():
    p0_script_client().dispatch(FireSceneToPositionCommand(None))



@router.get("/fire_to_position")
async def fire_scene_to_position(bar_length: int = 0):
    p0_script_client().dispatch(FireSceneToPositionCommand(bar_length))


@router.get("/fire_selected")
async def fire_selected_scene():
    p0_script_client().dispatch(FireSelectedSceneCommand())


@router.get("/scroll")
async def scroll_scenes(direction: str):
    p0_script_client().dispatch(ScrollScenesCommand(go_next=direction == "next"))


@router.get("/scroll_position")
async def scroll_scene_position(direction: str):
    p0_script_client().dispatch(ScrollScenePositionCommand(go_next=direction == "next"))


@router.get("/scroll_position_fine")
async def scroll_scene_position_fine(direction: str):
    p0_script_client().dispatch(
        ScrollScenePositionCommand(go_next=direction == "next", use_fine_scrolling=True)
    )


@router.get("/scroll_tracks")
async def scroll_scene_tracks(direction: str):
    p0_script_client().dispatch(ScrollSceneTracksCommand(go_next=direction == "next"))


@router.get("/duplicate")
async def duplicate_scene():
    p0_script_client().dispatch(DuplicateSceneCommand())
