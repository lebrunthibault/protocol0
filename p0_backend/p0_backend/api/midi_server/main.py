import signal
import sys
import time
import traceback

import mido
import requests
from loguru import logger
from mido import Message

from p0_backend.api.client.p0_script_api_client import p0_script_client
from p0_backend.celery.celery import check_celery_worker_status, notification_window
from p0_backend.lib.enum.notification_enum import NotificationEnum
from p0_backend.lib.midi.mido import _get_input_port
from p0_backend.lib.notification.notification.notification_factory import NotificationFactory
from p0_backend.lib.task_cache import TaskCache
from p0_backend.lib.timer import start_timer
from p0_backend.lib.utils import (
    log_string,
    make_dict_from_sysex_message,
    make_script_command_from_sysex_message,
)
from p0_backend.settings import Settings

logger = logger.opt(colors=True)

settings = Settings()


def start():
    system_check()

    midi_port_backend_loopback = mido.open_input(
        _get_input_port(settings.p0_backend_loopback_name), autoreset=False
    )
    midi_port_output = mido.open_input(
        _get_input_port(settings.p0_output_port_name), autoreset=False
    )

    logger.info(f"Midi server listening on {midi_port_backend_loopback} and {midi_port_output}")

    while True:
        _poll_midi_port(midi_port=midi_port_output)
        _poll_midi_port(midi_port=midi_port_backend_loopback)

        time.sleep(0.005)  # release cpu


def system_check():
    system_up = True

    if not check_celery_worker_status():
        start_timer(8, check_celery)

    try:
        requests.get(f"{settings.http_api_url}/")
    except requests.exceptions.ConnectionError:
        NotificationFactory.show_error("HTTP server is not up")
        system_up = False

    if system_up:
        logger.info("System is up")


def check_celery():
    TaskCache().clear()
    if not check_celery_worker_status():
        NotificationFactory.show_error("Celery is not up")


def signal_handler(*_):
    logger.warning("exiting after SIGINT")
    sys.exit()


signal.signal(signal.SIGINT, signal_handler)


def _poll_midi_port(midi_port):
    """non blocking poll"""
    while True:
        msg_output = midi_port.poll()
        if msg_output:
            try:
                _execute_midi_message(message=msg_output)
            except Exception as e:
                message = f"Midi server error\n\n{e}"
                message += traceback.format_exc()
                logger.error(log_string(message))
                logger.error(log_string(traceback.format_exc()))
                notification_window.delay(message, NotificationEnum.ERROR.value)
        else:
            break


def _execute_midi_message(message: Message):
    # shortcut to call directly the script api
    command = make_script_command_from_sysex_message(message=message)
    if command:
        p0_script_client().dispatch(command)
        return

    payload = make_dict_from_sysex_message(message=message)
    if not payload:
        return

    # or it can exploit the routes public API by passing an operation name
    method_name = payload["method"]
    args = payload["args"]

    if method_name == "post_set":
        requests.post(f"{settings.http_api_url}/set", json=args["ableton_set"])
        return

    requests.get(f"{settings.http_api_url}/{method_name}", params=args)
