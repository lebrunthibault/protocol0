from os.path import dirname

from fastapi import APIRouter
from loguru import logger
from pydantic import BaseModel

from p0_backend.lib.ableton.ableton import (
    open_set,
)
from p0_backend.lib.ableton.ableton_set.ableton_set import (
    AbletonSetCurrentState,
    AbletonTrack,
    PathInfo,
)
from p0_backend.lib.ableton.ableton_set.ableton_set_manager import (
    AbletonSetManager,
)
from p0_backend.lib.explorer import open_explorer
from p0_backend.settings import Settings

router = APIRouter()

settings = Settings()


class PostCurrentStatePayload(BaseModel):
    post_current_state_payload: AbletonSetCurrentState


# @router.post("/current_state", dependencies=[Depends(RateLimiter(times=1, milliseconds=50))])
@router.post("/current_state")
async def post_current_state(payload: PostCurrentStatePayload):
    await AbletonSetManager.create_from_current_state(payload.post_current_state_payload)


class UpdateTrackColorInnerPayload(BaseModel):
    track: AbletonTrack
    new_color: int


class UpdateTrackColorPayload(BaseModel):
    update_track_color_payload: UpdateTrackColorInnerPayload


@router.put("/track_color")
async def update_track_color(payload: UpdateTrackColorPayload):
    payload = payload.update_track_color_payload

    AbletonSetManager.update_track_color(payload.track, payload.new_color)


@router.post("/clear_state")
async def clear_state():
    AbletonSetManager.clear_state()


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


@router.get("/open_in_explorer")
async def open_in_explorer(path: str):
    open_explorer(dirname(PathInfo.create(path).filename))
