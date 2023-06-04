from time import sleep

from p0_backend.lib.ableton.interface.pixel import get_coords_for_color
from p0_backend.lib.ableton.interface.pixel_color_enum import PixelColorEnum
from p0_backend.lib.ableton.interface.track import click_context_menu
from p0_backend.lib.keys import send_keys
from p0_backend.lib.mouse.mouse import click, keep_mouse_position, get_mouse_position


@keep_mouse_position
def edit_automation_value():
    click_context_menu(get_mouse_position(), [-527, -510, -472, -416, -397, -396, -366, +2])


@keep_mouse_position
def set_envelope_loop_length(length: int):
    coords = get_coords_for_color(
        [PixelColorEnum.BUTTON_ACTIVATED_YELLOW],
        bbox=(100, 500, 600, 1030),
        from_bottom=True,
        from_right=True,
    )

    click(coords)
    x, y = coords

    # set the length
    click((x + 30, y))
    sleep(0.05)
    send_keys(str(length))
    sleep(0.05)
    send_keys("{ENTER}")
