from time import sleep
from typing import Callable

import pyautogui
import win32gui

from p0_backend.lib.keys import send_keys
from p0_backend.lib.mouse.mouse import drag_to, move_to, double_click, click
from p0_backend.lib.window.find_window import find_window_handle_by_enum


def _save_preset(x: int, y: int):
    sleep(0.1)
    click((x + 558, y + 57))
    sleep(0.5)
    send_keys("{ENTER}")
    sleep(0.2)
    click((x + 908, y + 454))


def _go_to_next_preset(x: int, y: int):
    sleep(0.2)
    click((x + 896, y + 69))
    sleep(0.2)


def _set_control_value(x: int, y: int, value: str, single_click: bool = False):
    if single_click:
        click((x, y))
    else:
        double_click((x, y))
    sleep(0.1)
    send_keys(value)
    send_keys("{ENTER}")
    sleep(0.1)


def _set_macro_1_value(x: int, y: int, value: str):
    click((x + 40, y + 582))
    sleep(0.5)
    _set_control_value(x + 40, y + 582, value)


def _rename_macro_1(x: int, y: int, name: str):
    _set_control_value(x + 60, y + 618, name, single_click=True)


def bulk_edit_presets(preset_edit_func: Callable[[int, int], None], test: bool = False):
    handle = find_window_handle_by_enum(name="Serum_x64/Midi")
    assert handle, "Serum window not found"
    x, y, x2, y2 = win32gui.GetWindowRect(handle)

    while win32gui.IsWindowVisible(handle):
        # make macro 1 bidirectional
        preset_edit_func(x, y)

        _save_preset(x, y)
        _go_to_next_preset(x, y)

        assert find_window_handle_by_enum(name="Serum_x64/Midi"), "Serum window not found"

        if test:
            break


def add_filter_macro(x: int, y: int) -> None:
    """Assign macro 1 to filter cutoff"""
    _set_macro_1_value(x, y, "0")
    _rename_macro_1(x, y, "FILTER")

    # assign macro 1 to filter cutoff
    move_to((x + 86, y + 590))
    drag_to((x + 976, y + 396), duration=0.2)


def make_filter_macro_bidirectional(x: int, y: int):
    """Make macro 1 (FILTER) assignment to filter bidirectional"""
    click((x + 86, y + 590))
    sleep(0.5)
    with pyautogui.hold("alt"):
        with pyautogui.hold("shift"):
            click((x + 976, y + 396))

    _set_macro_1_value(x, y, "50")


def set_preset_description(x: int, y: int, description: str):
    _set_control_value(x + 591, y + 98, description)
