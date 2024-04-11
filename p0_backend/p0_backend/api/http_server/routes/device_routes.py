from fastapi import APIRouter

from p0_backend.api.client.p0_script_api_client import p0_script_client
from p0_backend.lib.synth.serum import (
    bulk_edit_presets,
    set_preset_description,
)

from protocol0.application.command.LoadDeviceCommand import LoadDeviceCommand
from protocol0.application.command.LoadMinitaurCommand import LoadMinitaurCommand
from protocol0.application.command.LoadRev2Command import LoadRev2Command
from protocol0.application.command.ReloadGodParticleCommand import ReloadGodParticleCommand
from protocol0.application.command.ToggleRackChainCommand import ToggleRackChainCommand

router = APIRouter()


@router.get("/load")
async def load_device(name: str, create_track: bool = True):
    p0_script_client().dispatch(LoadDeviceCommand(name, create_track))


@router.get("/load_rev2")
async def load_rev2():
    p0_script_client().dispatch(LoadRev2Command())


@router.get("/load_minitaur")
async def load_minitaur():
    p0_script_client().dispatch(LoadMinitaurCommand())


@router.get("/reload_god_particle")
async def reload_god_particle():
    p0_script_client().dispatch(ReloadGodParticleCommand())


@router.get("/toggle_rack_chain")
async def toggle_rack_chain():
    p0_script_client().dispatch(ToggleRackChainCommand())


@router.get("/serum_bulk_edit")
async def serum_bulk_edit():
    # bulk_edit_presets(lambda x, y: set_preset_description(x, y, "Melodic Techno"))
    bulk_edit_presets(lambda x, y: set_preset_description(x, y, "Modern Melodic Techno", "PML"))
