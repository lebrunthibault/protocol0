from time import sleep

from p0_backend.lib.notification import notify
from p0_backend.lib.enum.notification_enum import NotificationEnum
from p0_backend.lib.keys import send_keys
from p0_backend.lib.mouse.mouse import click


def save_drum_rack(drum_rack_name: str):
    notify("Saving the drum rack", NotificationEnum.WARNING)
    click((351, 803))
    sleep(0.5)
    send_keys(drum_rack_name)
    sleep(0.5)
    send_keys("{ENTER}")
