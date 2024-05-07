from fastapi import APIRouter

from p0_backend.api.client.p0_script_api_client import p0_script_client
from p0_backend.lib.notification import notify
from p0_backend.lib.process import measure_cpu_usage
from protocol0.application.command.PlayPauseSongCommand import PlayPauseSongCommand

router = APIRouter()


@router.get("/measure_cpu_usage")
async def _measure_cpu_usage():
    p0_script_client().dispatch(PlayPauseSongCommand())

    cpu_usage = measure_cpu_usage()
    notify(f"Ableton Cpu usage : {cpu_usage}%")
