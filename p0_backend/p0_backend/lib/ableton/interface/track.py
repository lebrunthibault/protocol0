from typing import List, Union, Optional

import pyautogui

from p0_backend.lib.ableton.interface.coords import Coords
from p0_backend.lib.ableton.interface.pixel import (
    get_pixel_color_at,
    get_pixel_having_color,
)
from p0_backend.lib.ableton.interface.pixel_color_enum import PixelColorEnum
from p0_backend.lib.decorators import timeit
from p0_backend.lib.enum.notification_enum import NotificationEnum
from p0_backend.lib.mouse.mouse import click
from p0_backend.lib.notification import notify
from p0_backend.settings import Settings

settings = Settings()


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
