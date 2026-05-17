import asyncio
import traceback

import mido
import requests
from loguru import logger
from mido import Message

from p0_backend.api.client.p0_script_api_client import p0_script_client
from p0_backend.lib.enum.notification_enum import NotificationEnum
from p0_backend.lib.midi.mido import _get_input_port
from p0_backend.lib.notification import notify
from p0_backend.lib.utils import (
    log_string,
    make_dict_from_sysex_message,
    make_script_command_from_sysex_message,
)
from p0_backend.settings import Settings

logger = logger.opt(colors=True)

settings = Settings()


async def run_midi_listener() -> None:
    """Listen to MIDI input via rtmidi callback and dispatch messages asynchronously.

    The callback runs in rtmidi's internal thread; we hand messages off to the
    asyncio event loop via call_soon_threadsafe + asyncio.Queue, then consume
    them here.
    """
    loop = asyncio.get_running_loop()
    queue: asyncio.Queue[Message] = asyncio.Queue()

    def callback(message: Message) -> None:
        loop.call_soon_threadsafe(queue.put_nowait, message)

    port = mido.open_input(
        _get_input_port(settings.p0_output_port_name),
        callback=callback,
        autoreset=False,
    )
    logger.info(f"Midi server listening on {port}")

    try:
        while True:
            message = await queue.get()
            try:
                _execute_midi_message(message)
            except Exception as e:
                err = f"Midi server error\n\n{e}\n{traceback.format_exc()}"
                logger.error(log_string(err))
                notify(err, NotificationEnum.ERROR)
    except asyncio.CancelledError:
        raise
    finally:
        port.close()


def _execute_midi_message(message: Message) -> None:
    # shortcut to call directly the script api
    command = make_script_command_from_sysex_message(message=message)
    if command:
        p0_script_client().dispatch(command)
        return

    payload = make_dict_from_sysex_message(message=message)
    if not payload:
        return

    # or it can exploit the routes public API by passing an operation name
    method = payload["method"]
    path = payload["path"]
    params = payload["params"]

    endpoint = f"{settings.http_api_url}{path}"

    assert method in ("GET", "POST", "PUT", "DELETE"), f"unknown method {method}"

    if method == "GET":
        requests.get(endpoint, params=params)
    elif method == "POST":
        requests.post(endpoint, json=params)
    elif method == "PUT":
        requests.put(endpoint, json=params)
    elif method == "DELETE":
        requests.delete(endpoint, params=params)
