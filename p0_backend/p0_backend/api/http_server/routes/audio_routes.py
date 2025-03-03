from time import sleep

from fastapi import APIRouter

from p0_backend.lib.keys import send_keys

router = APIRouter()


@router.get("/restart_ableton_audio")
def restart_ableton_audio():
    send_keys("^+%e")
    sleep(2)
    send_keys("^+%e")
