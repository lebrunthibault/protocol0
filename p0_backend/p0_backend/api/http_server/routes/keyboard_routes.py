from time import sleep

from fastapi import APIRouter

from p0_backend.lib.keys import send_keys
from p0_backend.lib.mouse.mouse import click, click_vertical_zone, move_to, scroll

router = APIRouter()


@router.get("/move_to")
def _move_to(x: int, y: int):
    move_to((x, y))


@router.get("/click")
def _click(x: int, y: int):
    click((x, y))


@router.get("/click_vertical_zone")
def _click_vertical_zone(x: int, y: int):
    click_vertical_zone((x, y))


@router.get("/scroll")
def _scroll(steps: int = 1):
    scroll(steps)


@router.get("/select_and_copy")
def select_and_copy():
    send_keys("^a")
    send_keys("^c")


@router.get("/select_and_paste")
def select_and_paste():
    send_keys("^a")
    send_keys("^v")


@router.get("/search")
def search(text: str):
    send_keys("^f")
    sleep(0.1)
    send_keys(text)
