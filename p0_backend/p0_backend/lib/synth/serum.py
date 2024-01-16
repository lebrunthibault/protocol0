from time import sleep

import win32gui

from p0_backend.lib.keys import send_keys
from p0_backend.lib.mouse.mouse import drag_to, move_to, double_click, click
from p0_backend.lib.window.find_window import find_window_handle_by_enum


def serum_add_filter_macro():
    """Assign macro 1 to filter cutoff for all presets"""

    handle = find_window_handle_by_enum(name="Serum_x64/Midi")
    assert handle, "Serum window not found"
    x, y, x2, y2 = win32gui.GetWindowRect(handle)

    while win32gui.IsWindowVisible(handle):
        # reset macro 1
        click((x + 40, y + 582))
        sleep(0.5)
        double_click((x + 40, y + 582))
        sleep(0.1)
        send_keys("0")
        send_keys("{ENTER}")

        # rename macro 1
        click((x + 60, y + 618))
        sleep(0.1)
        send_keys("FILTER")
        send_keys("{ENTER}")
        sleep(0.1)

        # assign macro 1 to filter cutoff
        move_to((x + 86, y + 590))
        drag_to((x + 976, y + 396), duration=0.2)

        # save preset
        sleep(0.1)
        click((x + 558, y + 57))
        sleep(0.5)
        send_keys("{ENTER}")
        sleep(0.2)
        click((x + 908, y + 454))

        # go to next preset
        sleep(0.2)
        click((x + 896, y + 69))
        sleep(0.2)
