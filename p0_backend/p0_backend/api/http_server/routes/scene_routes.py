from fastapi import APIRouter

from p0_backend.api.client.p0_script_api_client import p0_script_client
from protocol0.application.command.ScrollScenesCommand import ScrollScenesCommand
from protocol0.application.command.ToggleSceneLoopCommand import ToggleSceneLoopCommand

router = APIRouter()


@router.get("/toggle_loop")
async def toggle_scene_loop():
    p0_script_client().dispatch(ToggleSceneLoopCommand())


@router.get("/scroll")
async def scroll_scenes(direction: str):
    p0_script_client().dispatch(ScrollScenesCommand(go_next=direction == "next"))
