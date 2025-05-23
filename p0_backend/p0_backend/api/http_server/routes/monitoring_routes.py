from typing import Optional

from fastapi import APIRouter

from p0_backend.api.client.p0_script_api_client import p0_script_client
from protocol0.application.command.SoloTracksCommand import SoloTracksCommand
from protocol0.application.command.ToggleBusCommand import ToggleBusCommand
from protocol0.application.command.ToggleExtOutCommand import ToggleExtOutCommand
from protocol0.application.command.ToggleReferenceTrackFiltersCommand import (
    ToggleReferenceTrackFiltersCommand,
)
from protocol0.application.command.ToggleReferenceTrackStereoModeCommand import (
    ToggleReferenceTrackStereoModeCommand,
)

router = APIRouter()


@router.get("/toggle_reference_filters")
async def toggle_reference_filters(preset: Optional[str] = None):
    p0_script_client().dispatch(ToggleReferenceTrackFiltersCommand(preset))


@router.get("/toggle_reference_stereo_mode")
async def toggle_reference_stereo_mode(stereo_mode: str):
    p0_script_client().dispatch(ToggleReferenceTrackStereoModeCommand(stereo_mode))


@router.get("/solo")
async def solo(solo_type: Optional[str] = None, bus_name: Optional[str] = None):
    p0_script_client().dispatch(SoloTracksCommand(solo_type, bus_name))


@router.get("/toggle_bus")
async def toggle_bus(bus_name: str):
    p0_script_client().dispatch(ToggleBusCommand(bus_name))


@router.get("/toggle_ext_out")
async def toggle_ext_out():
    p0_script_client().dispatch(ToggleExtOutCommand())
