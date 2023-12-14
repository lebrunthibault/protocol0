from fastapi import APIRouter

from backend.settings import Settings
from .set_routes import router as set_router

router = APIRouter()

settings = Settings()

router.include_router(set_router, prefix="/set")


@router.get("/")
def home() -> str:
    return "ok"
