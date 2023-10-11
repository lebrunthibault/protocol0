from itertools import chain
from typing import List, Dict

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
    set_stars,
    SceneStat,
)
from p0_backend.lib.ableton.ableton_set.ableton_set_manager import (
    AbletonSetManager,
    list_sets,
)
from p0_backend.settings import Settings
from protocol0.application.command.SaveSongCommand import SaveSongCommand

router = APIRouter()

settings = Settings()


@router.get("/all")
async def sets(archive: bool = False) -> Dict[str, List[AbletonSet]]:
    return list_sets(archive)


@router.get("")
async def get_set(path: str) -> AbletonSet:
    path = path.replace("\\\\", "\\")

    ableton_sets = list(chain.from_iterable(list_sets().values()))

    return next(s for s in ableton_sets if s.path_info.filename == path)


@router.post("")
async def post_set(ableton_set: AbletonSet):
    """Forwarded from midi server"""
    await AbletonSetManager.register(ableton_set)


@router.get("/close")
async def close_set(filename: str):
    await AbletonSetManager.remove(filename)
    await ws_manager.broadcast_server_state()


@router.post("/scene_stats")
async def post_scene_stats(scene_stats: List[SceneStat]):
    set_scene_stats(scene_stats)


class StarsPayload(BaseModel):
    stars: int


@router.post("/{filename}/stars")
async def post_set_stars(filename: str, stars: StarsPayload):
    set_stars(filename, stars.stars)


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
