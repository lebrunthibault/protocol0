from fastapi import APIRouter

from p0_backend.api.client.p0_script_api_client import p0_script_client
from protocol0.application.command.CaptureMidiCommand import CaptureMidiCommand
from protocol0.application.command.CaptureMidiValidateCommand import CaptureMidiValidateCommand
from protocol0.application.command.RecordUnlimitedCommand import RecordUnlimitedCommand

router = APIRouter()


@router.get("/unlimited")
async def record_unlimited():
    p0_script_client().dispatch(RecordUnlimitedCommand())


@router.get("/capture_midi")
async def capture_midi():
    p0_script_client().dispatch(CaptureMidiCommand())


@router.get("/capture_midi/validate")
async def capture_midi_validate():
    p0_script_client().dispatch(CaptureMidiValidateCommand())
