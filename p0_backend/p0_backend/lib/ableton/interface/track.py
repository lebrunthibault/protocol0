from time import sleep
from typing import List, Union, Optional

import pyautogui

from p0_backend.api.client.p0_script_api_client import p0_script_client
from p0_backend.lib.ableton.get_set import get_ableton_window_titles
from p0_backend.lib.ableton.interface.coords import Coords
from p0_backend.lib.ableton.interface.pixel import (
    get_pixel_color_at,
    get_coords_for_color,
    get_pixel_having_color,
)
from p0_backend.lib.ableton.interface.pixel_color_enum import PixelColorEnum
from p0_backend.lib.decorators import timeit
from p0_backend.lib.enum.notification_enum import NotificationEnum
from p0_backend.lib.explorer import drag_file_to
from p0_backend.lib.mouse.mouse import click
from p0_backend.lib.notification import notify
from p0_backend.settings import Settings, DOWN_BBOX
from protocol0.application.command.EmitBackendEventCommand import (
    EmitBackendEventCommand,
)

settings = Settings()


def get_focused_track_coords(box_boundary="left") -> Coords:
    x, y = get_coords_for_color(
        [PixelColorEnum.ELEMENT_FOCUSED, PixelColorEnum.ELEMENT_SELECTED],
        # bbox=(40, 45, 1870, 110), # session view
        bbox=(1502, 108, 1800, 720),
        from_right=box_boundary == "right",
    )
    p0_script_client().dispatch(EmitBackendEventCommand("track_focused"))

    return x + 30, y + 5  # drag works better here


@timeit
def click_context_menu(track_coords: Coords, y_offsets: Union[int, List[int]]) -> Optional[Coords]:
    y_offsets = [y_offsets] if isinstance(y_offsets, int) else y_offsets

    click(track_coords, button=pyautogui.RIGHT)

    x, y = track_coords

    separator_coords_list = []

    for y_offset in y_offsets:
        # left and right
        separator_coords_list += [(x - 10, y + y_offset), (x + 10, y + y_offset)]

    separator_coords = get_pixel_having_color(separator_coords_list, is_black=True, debug=False)

    if separator_coords is None:
        notify("context menu not detected (separator)", NotificationEnum.WARNING)
        return 0, 0

    x_separator, y_separator = separator_coords
    menu_coords = (x_separator, y_separator + 10)

    if get_pixel_color_at(menu_coords) != PixelColorEnum.context_menu_background():
        notify(
            "context menu not detected (background)",
            NotificationEnum.WARNING,
        )
        return 0, 0

    click(menu_coords)

    return menu_coords


def freeze_track():
    track_coords = get_focused_track_coords()

    freeze_coords = click_context_menu(track_coords, [98, 136, 137])

    if freeze_coords is None:
        return

    sleep(0.2)

    # wait for track freeze
    while "Freeze..." in get_ableton_window_titles():
        sleep(0.2)

    sleep(0.3)

    p0_script_client().dispatch(EmitBackendEventCommand("track_freezed"))

    return freeze_coords


def flatten_track():
    track_coords = get_focused_track_coords()

    freeze_coords = freeze_track()

    click(track_coords, button=pyautogui.RIGHT)
    click((freeze_coords[0], freeze_coords[1] + 20))  # flatten track

    p0_script_client().dispatch(EmitBackendEventCommand("track_flattened"))


def add_track_to_selection():
    track_coords = get_focused_track_coords()
    click(track_coords)

    p0_script_client().dispatch(EmitBackendEventCommand("track_selected"))


def load_instrument_track(instrument_name: str):
    track_path = f"{settings.ableton_set_directory}\\{settings.instrument_tracks_folder}\\{instrument_name}.als"

    drag_file_to(
        track_path,
        get_focused_track_coords(box_boundary="right"),
        bbox=DOWN_BBOX,
        drag_duration=0.2,
        close_window=False,
    )

    p0_script_client().dispatch(EmitBackendEventCommand("instrument_loaded"))
