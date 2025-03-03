from time import sleep

from fastapi import APIRouter

from p0_backend.lib.keys import send_keys
from p0_backend.lib.mouse.mouse import click, move_to, scroll

router = APIRouter()


@router.get("/move_to")
def _move_to(x: int, y: int):
    move_to((x, y))


@router.get("/click")
def _click(x: int, y: int):
    click((x, y))


@router.get("/scroll")
def _scroll(pixels: int = 1):
    scroll(pixels)


@router.get("/search")
def search(text: str):
    send_keys("^f")
    sleep(0.1)
    send_keys(text)


@router.get("/shift_down")
def shift_down():
    send_keys("+{DOWN}")
