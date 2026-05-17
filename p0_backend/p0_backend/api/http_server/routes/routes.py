from fastapi import APIRouter
from win11toast import toast_async

from p0_backend.api.client.p0_script_api_client import p0_script_client
from p0_backend.lib.ableton.ableton import (
    reload_ableton,
    hide_plugins,
    show_plugins,
)
from p0_backend.lib.enum.notification_enum import NotificationEnum
from p0_backend.lib.keys import send_keys
from p0_backend.lib.notification import notify
from p0_backend.lib.process import execute_powershell_command
from p0_backend.lib.window.find_window import find_window_handle_by_enum
from p0_backend.lib.window.window import focus_window
from p0_backend.settings import Settings

from .clip_routes import router as clip_router
from .device_routes import router as device_router
from .search_routes import router as search_router
from .set_routes import router as set_router

router = APIRouter()

settings = Settings()

router.include_router(clip_router, prefix="/clip")
router.include_router(device_router, prefix="/device")
router.include_router(search_router, prefix="/search")
router.include_router(set_router, prefix="/set")


@router.get("/")
def home() -> str:
    return "ok"


@router.get("/ping")
def ping() -> str:
    return "pong"


@router.get("/reload_ableton")
async def _reload_ableton():
    reload_ableton()


@router.get("/show_plugins")
def _show_plugins():
    show_plugins()


@router.get("/show_hide_plugins")
def show_hide_plugins():
    send_keys("^%p")


@router.get("/hide_plugins")
def _hide_plugins():
    hide_plugins()


@router.get("/show_info")
def show_info(message: str):
    notify(message, NotificationEnum.INFO)


@router.get("/show_success")
def show_success(message: str):
    notify(message, NotificationEnum.SUCCESS)


@router.get("/show_warning")
def show_warning(message: str):
    notify(message, NotificationEnum.WARNING)


@router.get("/show_error")
async def show_error(message: str):
    await toast_async(message)


@router.get("/tail_logs")
async def tail_logs():
    if find_window_handle_by_enum(settings.log_window_title):
        focus_window(settings.log_window_title)
        return

    execute_powershell_command("poetry run logs")


@router.get("/tail_logs_raw")
async def tail_logs_raw():
    execute_powershell_command("poetry run logs-raw")


@router.get("/play_pause")
async def play_pause():
    p0_script_client().play_pause()


@router.get("/log_selected")
async def _log_selected():
    p0_script_client().log_selected()


@router.get("/log_song_stats")
async def _log_song_stats():
    p0_script_client().log_song_stats()
