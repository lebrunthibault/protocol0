from fastapi import APIRouter

from p0_backend.api.client.p0_script_api_client import p0_script_client
from p0_backend.lib.ableton.ableton import (
    hide_plugins,
    show_plugins,
)
from p0_backend.lib.keys import send_keys
from protocol0.application.command.BusTrackToZeroDBCommand import BusTrackToZeroDBCommand
from protocol0.application.command.ChangeTrackSoundCommand import ChangeTrackSoundCommand
from protocol0.application.command.CollapseSelectedTrackCommand import CollapseSelectedTrackCommand

router = APIRouter()


@router.get("/un_group")
async def un_group():
    hide_plugins()
    send_keys("+{TAB}")
    send_keys("+{TAB}")
    send_keys("^+g")
    show_plugins()


@router.get("/collapse_selected")
async def collapse_selected():
    p0_script_client().dispatch(CollapseSelectedTrackCommand())


@router.get("/bus_to_zero_db")
async def bus_to_zero_db():
    p0_script_client().dispatch(BusTrackToZeroDBCommand())


@router.get("/change_sound")
async def change_track_sound(track_type: str, index: int):
    p0_script_client().dispatch(ChangeTrackSoundCommand(track_type, index))
