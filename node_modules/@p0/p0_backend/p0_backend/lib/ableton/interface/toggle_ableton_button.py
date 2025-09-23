from p0_backend.api.client.p0_script_api_client import p0_script_client
from p0_backend.lib.ableton.interface.coords import Coords
from p0_backend.lib.mouse.mouse import click, keep_mouse_position
from protocol0.application.command.EmitBackendEventCommand import (
    EmitBackendEventCommand,
)


@keep_mouse_position
def toggle_ableton_button(coords: Coords) -> None:
    click(coords, duration=0.1)
    p0_script_client().dispatch(EmitBackendEventCommand("button_toggled"))
