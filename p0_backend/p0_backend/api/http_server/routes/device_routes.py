import subprocess

from fastapi import APIRouter

from p0_backend.api.client.p0_script_api_client import p0_script_client
from p0_backend.lib.ableton.interface.toggle_ableton_button import toggle_ableton_button
from p0_backend.lib.synth.serum import (
    bulk_edit_presets,
    set_preset_description,
)
from p0_backend.settings import Settings
from protocol0.application.command.LoadDeviceCommand import LoadDeviceCommand
from protocol0.application.command.ReloadGodParticleCommand import ReloadGodParticleCommand
from protocol0.application.command.ToggleCpuHeavyDevicesCommand import ToggleCpuHeavyDevicesCommand
from protocol0.application.command.ToggleRackChainCommand import ToggleRackChainCommand

router = APIRouter()

settings = Settings()


@router.get("/load")
async def load_device(name: str):
    p0_script_client().dispatch(LoadDeviceCommand(name))

    if name == "SPLICE_BRIDGE":
        # will focus if it's hidden or in sys tray
        subprocess.run(settings.splice_executable)


@router.get("/reload_god_particle")
async def reload_god_particle():
    p0_script_client().dispatch(ReloadGodParticleCommand())


@router.get("/toggle_cpu_heavy")
async def toggle_cpu_heavy():
    p0_script_client().dispatch(ToggleCpuHeavyDevicesCommand())


@router.get("/toggle_rack_chain")
async def toggle_rack_chain():
    p0_script_client().dispatch(ToggleRackChainCommand())


@router.get("/toggle_ableton_button")
def _toggle_ableton_button(x: int, y: int):
    toggle_ableton_button((x, y))


@router.get("/serum_bulk_edit")
async def serum_bulk_edit():
    # bulk_edit_presets(lambda x, y: set_preset_description(x, y, "Melodic Techno"))
    bulk_edit_presets(lambda x, y: set_preset_description(x, y, "Modern Melodic Techno", "PML"))
