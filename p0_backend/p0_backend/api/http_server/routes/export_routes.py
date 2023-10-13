from fastapi import APIRouter
from p0_backend.api.client.p0_script_api_client import p0_script_client
from p0_backend.lib.ableton.ableton import export_audio
from protocol0.application.command.ExportAudioCommand import ExportAudioCommand

router = APIRouter()


@router.get("/")
async def export():
    p0_script_client().dispatch(ExportAudioCommand())


@router.get("/audio")
async def _export_audio():
    export_audio()
