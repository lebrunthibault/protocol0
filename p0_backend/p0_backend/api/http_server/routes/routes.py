from fastapi import APIRouter

from p0_backend.lib.process import execute_powershell_command
from p0_backend.lib.window.find_window import find_window_handle_by_enum
from p0_backend.lib.window.window import focus_window
from p0_backend.settings import Settings

from .clip_routes import router as clip_router
from .device_routes import router as device_router
from .search_routes import router as search_router

router = APIRouter()

settings = Settings()

router.include_router(clip_router, prefix="/clip")
router.include_router(device_router, prefix="/device")
router.include_router(search_router, prefix="/search")


@router.get("/")
def home() -> str:
    return "ok"


@router.get("/ping")
def ping() -> str:
    return "pong"


@router.get("/tail_logs")
async def tail_logs():
    if find_window_handle_by_enum(settings.log_window_title):
        focus_window(settings.log_window_title)
        return

    execute_powershell_command("poetry run logs")
