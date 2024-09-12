from threading import Thread
from typing import Optional

from fastapi import APIRouter

from p0_backend.api.client.p0_script_api_client import p0_script_client
from p0_backend.lib.search.search_gui import create_thread
from p0_backend.lib.search.search_queue import search_queue
from protocol0.application.command.ToggleFollowSongCommand import ToggleFollowSongCommand

router = APIRouter()
thread: Optional[Thread] = None
track_list_search_history: set[str] = set()
selected_track: Optional[str] = None


@router.get("/track")
async def _search_track(reset: bool = False) -> None:
    p0_script_client().dispatch(ToggleFollowSongCommand())

    create_thread(reset)
    search_queue.put("show_window")
