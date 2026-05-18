from time import sleep

from backend.lib.keys import send_keys
from backend.lib.mouse.mouse import click


def save_drum_rack(drum_rack_name: str):
    click((351, 803))
    sleep(0.5)
    send_keys(drum_rack_name)
    sleep(0.5)
    send_keys("{ENTER}")
