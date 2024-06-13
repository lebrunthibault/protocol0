from fastapi import APIRouter

from p0_backend.api.client.p0_script_api_client import p0_script_client
from p0_backend.lib.ableton.ableton import (
    hide_plugins,
    show_plugins,
)
from p0_backend.lib.ableton.interface.track import (
    flatten_track,
    load_instrument_track,
    freeze_track,
    add_track_to_selection,
)
from p0_backend.lib.keys import send_keys
from protocol0.application.command.BusTrackToZeroDBCommand import BusTrackToZeroDBCommand
from protocol0.application.command.CollapseSelectedTrackCommand import CollapseSelectedTrackCommand
from protocol0.application.command.SelectTrackCommand import SelectTrackCommand
from protocol0.application.command.ToggleArmCommand import ToggleArmCommand

router = APIRouter()


@router.get("/freeze")
def _freeze_track():
    freeze_track()


@router.get("/flatten")
def _flatten_track():
    flatten_track()


@router.get("/add_track_to_selection")
def _add_track_to_selection():
    add_track_to_selection()


@router.get("/un_group")
async def un_group():
    hide_plugins()
    send_keys("+{TAB}")
    send_keys("+{TAB}")
    send_keys("^+g")
    show_plugins()


@router.get("/load_instrument_track")
def _load_instrument_track(instrument_name: str):
    load_instrument_track(instrument_name)


@router.get("/arm")
async def arm():
    p0_script_client().dispatch(ToggleArmCommand())


@router.get("/select")
async def select(name: str):
    p0_script_client().dispatch(SelectTrackCommand(name.upper()))


@router.get("/collapse_selected")
async def collapse_selected():
    p0_script_client().dispatch(CollapseSelectedTrackCommand())


@router.get("/bus_to_zero_db")
async def bus_to_zero_db():
    p0_script_client().dispatch(BusTrackToZeroDBCommand())
