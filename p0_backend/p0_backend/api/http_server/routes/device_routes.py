from fastapi import APIRouter

from p0_backend.api.client.p0_script_api_client import p0_script_client
from protocol0.application.command.LoadDeviceCommand import LoadDeviceCommand

router = APIRouter()


@router.get("/load")
async def load_device(name: str):
    p0_script_client().dispatch(LoadDeviceCommand(name))
