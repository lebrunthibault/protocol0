from p0_backend.lib.ableton.interface.track import click_context_menu
from p0_backend.lib.mouse.mouse import keep_mouse_position, get_mouse_position


@keep_mouse_position
def edit_automation_value():
    click_context_menu(get_mouse_position(), [-527, -510, -472, -416, -397, -396, -366, +2])
