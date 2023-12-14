from fastapi import APIRouter

from backend.settings import Settings
from .set_routes import router as set_router
from .settings_routes import router as settings_router

router = APIRouter()

settings = Settings()

router.include_router(set_router, prefix="/set")
router.include_router(settings_router, prefix="/settings")


@router.get("/")
def home() -> str:
    return "ok"
