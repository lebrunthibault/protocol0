from functools import wraps
from time import sleep
import win32api
from win32con import MOUSEEVENTF_WHEEL

import pyautogui
from loguru import logger

from p0_backend.lib.ableton.interface.coords import Coords


def move_to(coords: Coords) -> None:
    pyautogui.moveTo(*coords)


def tween(n: float) -> float:
    """mouse go fast then slow"""
    return 1 - pow(n - 1, 6)


def drag_to(coords: Coords, duration=0.5) -> None:
    pyautogui.dragTo(*coords, button="left", duration=duration, tween=tween)


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


def double_click(coords: Coords, interval: float = 0) -> None:
    x, y = coords
    pyautogui.doubleClick(x, y, interval=interval)


def click_vertical_zone(coords: Coords) -> None:
    x, y = coords
    for i in range(120, -40, -20):
        pyautogui.click(x, y + i)


def scroll(pixels: int):
    win32api.mouse_event(MOUSEEVENTF_WHEEL, 960, 540, pixels, 0)


def get_mouse_position() -> Coords:
    return pyautogui.position()


def keep_mouse_position(func):
    @wraps(func)
    def decorate(*a, **k):
        coords = get_mouse_position()

        res = func(*a, **k)

        move_to(coords)

        return res

    return decorate
