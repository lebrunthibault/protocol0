import os
from os.path import basename
from time import sleep

import win32gui

from p0_backend.lib.ableton.interface.coords import Coords, RectCoords
from p0_backend.lib.ableton.interface.pixel import (
    get_coords_for_color,
)
from p0_backend.lib.ableton.interface.pixel_color_enum import PixelColorEnum
from p0_backend.lib.decorators import retry
from p0_backend.lib.errors.Protocol0Error import Protocol0Error
from p0_backend.lib.mouse.mouse import click, drag_to, move_to
from p0_backend.lib.process import kill_window_by_criteria
from p0_backend.lib.window.window import focus_window, move_window, window_contains_coords


def open_explorer(file_path: str) -> int:
    assert os.path.exists(file_path), f"'{file_path}' does not exist"

    click((0, 500))  # move the cursor from the explorer window position
    folder_name = basename(os.path.split(file_path)[0])
    try:
        handle = focus_window(folder_name)
        sleep(0.1)
        return handle
    except (AssertionError, Protocol0Error):
        os.system(f"explorer.exe /select, {file_path}")
        handle = retry(50, 0.1)(focus_window)(name=folder_name)
        sleep(0.5)

    return handle


@retry(2, 0)
def _open_explorer_until_selected(file_path: str, bbox: RectCoords, dest_coords: Coords):
    handle = open_explorer(file_path)

    window_bbox = win32gui.GetWindowRect(handle)

    # move window if its in the way
    if window_contains_coords(window_bbox, dest_coords):
        move_window(handle, bbox)
        window_bbox = bbox

    x, y, x2, y2 = window_bbox

    try:
        return retry(3, 0)(get_coords_for_color)(
            [
                PixelColorEnum.EXPLORER_SELECTED_ENTRY,
                PixelColorEnum.EXPLORER_SELECTED_ENTRY_LIGHT,
            ],
            bbox=(x + 200, y + 200, x2, y2),
        )
    except Protocol0Error as e:
        close_samples_windows()
        raise e


def drag_file_to(
    file_path: str,
    dest_coords: Coords,
    bbox: RectCoords,
    drag_duration=0.5,
    close_window=True,
):
    x, y = _open_explorer_until_selected(file_path, bbox, dest_coords)

    move_to((x, y + 10))
    drag_to(dest_coords, duration=drag_duration)

    if close_window:
        folder_name = basename(os.path.split(file_path)[0])

        kill_window_by_criteria(name=folder_name)


def close_samples_windows():
    kill_window_by_criteria(name="Recorded")
    kill_window_by_criteria(name="Freeze")


def close_explorer_window(title: str):
    kill_window_by_criteria(name=title)
