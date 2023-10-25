from typing import List

from fastapi import APIRouter
from loguru import logger
from pydantic import BaseModel

from p0_backend.api.client.p0_script_api_client import p0_script_client
from p0_backend.api.http_server.ws import ws_manager
from p0_backend.lib.ableton.ableton import (
    open_set,
)
from p0_backend.lib.ableton.ableton import (
    save_set_as_template,
)
from p0_backend.lib.ableton.ableton_set.ableton_set import (
    AbletonSet,
    set_scene_stats,
    SceneStat,
    SetPayload,
    update_set,
    move_set,
    AbletonSetCurrentState,
)
from p0_backend.lib.ableton.ableton_set.ableton_set_manager import (
    AbletonSetManager,
    list_sets,
    AbletonSetPlace,
)
from p0_backend.settings import Settings
from protocol0.application.command.SaveSongCommand import SaveSongCommand

router = APIRouter()

settings = Settings()


@router.get("/all")
async def sets(place: AbletonSetPlace = AbletonSetPlace.TRACKS) -> List[AbletonSet]:
    return list_sets(place)


class PostCurrentStatePayload(BaseModel):
    post_current_state_payload: AbletonSetCurrentState


@router.post("/current_state")
async def post_current_state(payload: PostCurrentStatePayload):
    await AbletonSetManager.create_from_current_state(payload.post_current_state_payload)


class PostSceneStatsPayload(BaseModel):
    post_scene_stats_payload: List[SceneStat]


@router.post("/scene_stats")
async def post_scene_stats(payload: PostSceneStatsPayload):
    set_scene_stats(payload.post_scene_stats_payload)


@router.put("/{filename}")
async def put_set(filename: str, payload: SetPayload):
    update_set(filename, payload)


@router.get("/save_as_template")
async def _save_set_as_template():
    save_set_as_template()


@router.get("/save")
async def save_set():
    p0_script_client().dispatch(SaveSongCommand())


@router.get("/open")
async def _open_set(path: str):
    open_set(path)


@router.get("/open_by_type")
async def open_set_by_type(name: str):
    if name == "default":
        open_set(f"{settings.ableton_set_directory}\\Default.als")
    else:
        logger.error(f"Unknown set type {name}")


@router.get("/close")
async def close_set(filename: str):
    await AbletonSetManager.remove(filename)
    await ws_manager.broadcast_server_state()


@router.post("/archive")
async def _archive_set(path: str):
    move_set(path, AbletonSetPlace.ARCHIVE)


@router.post("/un_archive")
async def _un_archive_set(path: str):
    move_set(path, AbletonSetPlace.TRACKS)


@router.delete("")
async def _delete_set(path: str):
    move_set(path, AbletonSetPlace.TRASH)
