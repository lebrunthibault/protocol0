from time import sleep

import pyautogui
from loguru import logger

from backend.lib.ableton.interface.coords import Coords


def click(coords: Coords, button=pyautogui.PRIMARY, duration=0) -> None:
    # coordinates are relative to a 1080p display resolution
    # accounting for resolution change

    x, y = coords

    try:
        pyautogui.mouseDown(x, y, button=button)
        sleep(duration)
        pyautogui.mouseUp(x, y, button=button)
    except pyautogui.FailSafeException as e:
        logger.warning(e)
