from time import sleep

from p0_backend.lib.ableton.interface.coords import CoordsEnum
from p0_backend.lib.ableton.interface.pixel import get_pixel_color_at
from p0_backend.lib.ableton.interface.pixel_color_enum import PixelColorEnum
from p0_backend.lib.keys import send_keys, send_down, send_right
from p0_backend.lib.mouse.mouse import click, double_click


def toggle_browser():
    send_keys("^%b")
    sleep(0.1)


def is_browser_visible() -> bool:
    return get_pixel_color_at(CoordsEnum.browser_left_size()) == PixelColorEnum.browser_background()


def click_browser_tracks():
    if not is_browser_visible():
        toggle_browser()

    coords = CoordsEnum.browser_place_tracks()
    if get_pixel_color_at(CoordsEnum.BROWSER_ALL_RESULTS.value) == PixelColorEnum.BLACK:
        coords = CoordsEnum.BROWSER_PLACE_TRACKS_2.value

    assert is_browser_visible(), "Browser is not selectable"

    double_click(coords)


def search(search: str):
    send_keys("^f")
    sleep(0.1)
    send_keys(search)


def preload_sample_category(category: str):
    search("")  # focus the browser
    sleep(0.1)
    click(CoordsEnum.BROWSER_PLACE_IMPORTED.value)  # click on samples folder in browser
    sleep(0.05)
    click(
        CoordsEnum.BROWSER_SEARCH_BOX.value
    )  # click in the search box without activating search mode
    sleep(0.05)
    send_keys("^a")
    send_keys("{BACKSPACE}")
    send_keys(f"'{category}'")  # filter on the set folder
    sleep(0.2)

    # a way to always show the tracks sub folder
    send_down()

    send_right()
