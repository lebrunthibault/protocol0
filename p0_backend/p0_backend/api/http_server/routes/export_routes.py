from fastapi import APIRouter

from p0_backend.api.client.p0_script_api_client import p0_script_client
from protocol0.application.command.OnExportCommand import OnExportCommand
from protocol0.application.command.WriteSessionToArrangementCommand import (
    WriteSessionToArrangementCommand,
)

router = APIRouter()


@router.get("/write_session_to_arrangement")
async def export():
    p0_script_client().dispatch(WriteSessionToArrangementCommand())


@router.get("/")
async def on_export():
    p0_script_client().dispatch(OnExportCommand())
