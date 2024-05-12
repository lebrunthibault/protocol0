from time import sleep

from p0_backend.lib.keys import send_keys


def search(keys: str):
    send_keys("^f")
    sleep(0.1)
    send_keys(keys)
