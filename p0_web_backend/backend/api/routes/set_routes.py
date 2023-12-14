from typing import List

from fastapi import APIRouter

from backend.lib.ableton.ableton_set import (
    AbletonSet,
    SetPayload,
    update_set,
    move_set,
    list_sets,
    AbletonSetPlace,
)
from backend.settings import Settings

router = APIRouter()

settings = Settings()

try:
    from p0_backend.lib.ableton.ableton import open_set
except ImportError:

    def open_set(*_, **__):
        pass


@router.get("/all")
async def sets(place: AbletonSetPlace = AbletonSetPlace.TRACKS) -> List[AbletonSet]:
    return list_sets(place)


@router.put("/{filename}")
async def put_set(filename: str, payload: SetPayload):
    update_set(filename, payload)


@router.get("/open")
async def _open_set(path: str):
    open_set(path)


@router.post("/archive")
async def _archive_set(path: str):
    move_set(path, AbletonSetPlace.ARCHIVE)


@router.post("/un_archive")
async def _un_archive_set(path: str):
    move_set(path, AbletonSetPlace.TRACKS)


@router.delete("")
async def _delete_set(path: str):
    move_set(path, AbletonSetPlace.TRASH)
