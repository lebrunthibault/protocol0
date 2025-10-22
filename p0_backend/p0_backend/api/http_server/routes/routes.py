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

from protocol0.application.command.BackendPongCommand import BackendPongCommand
from protocol0.application.command.LogSelectedCommand import LogSelectedCommand
from protocol0.application.command.LogSongStatsCommand import LogSongStatsCommand
from protocol0.application.command.PlayPauseSongCommand import PlayPauseSongCommand
from .action_routes import router as action_router
from .clip_routes import router as clip_router
from .device_routes import router as device_router
from .export_routes import router as export_router
from .keyboard_routes import router as keyboard_router
from .monitoring_routes import router as monitoring_router
from .process_routes import router as process_router
from .search_routes import router as search_router
from .set_routes import router as set_router
from .track_routes import router as track_router

router = APIRouter()

settings = Settings()

router.include_router(action_router, prefix="/actions")
router.include_router(clip_router, prefix="/clip")
router.include_router(device_router, prefix="/device")
router.include_router(export_router, prefix="/export")
router.include_router(keyboard_router, prefix="/keyboard")
router.include_router(monitoring_router, prefix="/monitoring")
router.include_router(process_router, prefix="/process")
router.include_router(search_router, prefix="/search")
router.include_router(set_router, prefix="/set")
router.include_router(track_router, prefix="/track")


@router.get("/")
def home() -> str:
    return "ok"


@router.get("/ping")
def ping() -> None:
    p0_script_client().dispatch(BackendPongCommand())


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
    p0_script_client().dispatch(PlayPauseSongCommand())


@router.get("/log_selected")
async def _log_selected():
    p0_script_client().dispatch(LogSelectedCommand())


@router.get("/log_song_stats")
async def _log_song_stats():
    p0_script_client().dispatch(LogSongStatsCommand())
