from time import sleep

from p0_backend.lib.ableton.interface.coords import CoordsEnum
from p0_backend.lib.keys import send_keys, send_down, send_right
from p0_backend.lib.mouse.mouse import click


def search(keys: str):
    send_keys("^f")
    sleep(0.1)
    send_keys(keys)


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
