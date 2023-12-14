from fastapi import APIRouter

from backend.settings import DirectorySettings, load_settings, save_settings

router = APIRouter()
settings = load_settings()


@router.get("/")
async def get_settings() -> DirectorySettings:
    return settings.directories


@router.put("/")
async def put_settings(settings_payload: DirectorySettings):
    settings.directories = settings_payload
    save_settings(settings)
