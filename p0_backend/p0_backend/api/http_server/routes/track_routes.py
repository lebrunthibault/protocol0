from fastapi import APIRouter

from p0_backend.api.client.p0_script_api_client import p0_script_client
from p0_backend.lib.ableton.ableton import (
    hide_plugins,
    show_plugins,
)
from p0_backend.lib.ableton.interface.track import flatten_track, load_instrument_track
from p0_backend.lib.keys import send_keys
from protocol0.application.command.ToggleArmCommand import ToggleArmCommand
from protocol0.application.command.SelectTrackCommand import SelectTrackCommand

router = APIRouter()


@router.get("/flatten_track")
def _flatten_track():
    flatten_track()


@router.get("/un_group")
async def un_group():
    hide_plugins()
    send_keys("+{TAB}")
    send_keys("+{TAB}")
    send_keys("^+g")
    show_plugins(force=True)


@router.get("/load_instrument_track")
def _load_instrument_track(instrument_name: str):
    load_instrument_track(instrument_name)


@router.get("/arm")
async def arm():
    p0_script_client().dispatch(ToggleArmCommand())


@router.get("/select")
async def select(name: str):
    p0_script_client().dispatch(SelectTrackCommand(name.replace("_", " ")))
