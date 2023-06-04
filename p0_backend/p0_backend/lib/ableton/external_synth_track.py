from p0_backend.api.settings import Settings
from p0_backend.lib.ableton.ableton import show_plugins
from p0_backend.lib.ableton.interface.coords import CoordsEnum, Coords
from p0_backend.lib.ableton.interface.pixel import get_absolute_coords
from p0_backend.lib.mouse.mouse import click
from p0_backend.lib.window.find_window import find_window_handle_by_enum
from p0_backend.lib.window.window import focus_window

settings = Settings()


def activate_rev2_editor():
    _click_rev2_editor(CoordsEnum.REV2_ACTIVATION_MIDDLE_BUTTON.value)


def post_activate_rev2_editor():
    _click_rev2_editor(CoordsEnum.REV2_PROGRAM.value)


def _click_rev2_editor(coords: Coords):
    show_plugins()
    handle = find_window_handle_by_enum(settings.rev2_editor_window_title)
    assert handle, "Couldn't focus rev2 editor"
    focus_window(name=settings.rev2_editor_window_title)
    click(get_absolute_coords(handle, coords), exact=True)
