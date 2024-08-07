import os
import time

import keyboard
import win32gui  # noqa
from loguru import logger
from ratelimit import limits

from p0_backend.api.client.p0_script_api_client import p0_script_client
from p0_backend.lib.ableton.ableton_set.ableton_set import PathInfo
from p0_backend.lib.ableton.interface.pixel import get_pixel_color_at
from p0_backend.lib.ableton.interface.pixel_color_enum import PixelColorEnum
from p0_backend.lib.enum.notification_enum import NotificationEnum
from p0_backend.lib.errors.Protocol0Error import Protocol0Error
from p0_backend.lib.keys import send_keys
from p0_backend.lib.keys import send_right
from p0_backend.lib.mouse.mouse import click, keep_mouse_position
from p0_backend.lib.notification import notify
from p0_backend.lib.process import execute_powershell_command, kill_window_by_criteria
from p0_backend.lib.window.find_window import find_window_handle_by_enum, SearchTypeEnum
from p0_backend.lib.window.window import (
    focus_window,
    get_focused_window_process_name,
)
from p0_backend.settings import Settings
from protocol0.application.command.ResetPlaybackCommand import ResetPlaybackCommand

settings = Settings()


def focus_ableton() -> None:
    focus_window(
        settings.ableton_process_name, search_type=SearchTypeEnum.PROGRAM_NAME
    )  # type: ignore


def is_ableton_focused() -> bool:
    return get_focused_window_process_name() == settings.ableton_process_name


def plugins_shown() -> bool:
    return bool(
        find_window_handle_by_enum(
            "AbletonVstPlugClass", search_type=SearchTypeEnum.WINDOW_CLASS_NAME
        )
    )


def show_plugins() -> None:
    # if force or not plugins_shown():
    keyboard.press_and_release("ctrl+alt+p")


def hide_plugins():
    if plugins_shown():
        send_keys("^%p")


@limits(calls=1, period=5)
def reload_ableton() -> None:
    """
    Not easy to have this work every time
    """
    # execute_powershell_command(
    #     f'& "D:\\SoundBanks and programs\\Ableton 10\\Program\\Ableton Live 10 Suite.exe" "C:\\Users\\thiba\\OneDrive\\Bureau\\default 10 Project\\default 10.als"',
    #     minimized=True,
    # )
    # return
    try:
        focus_ableton()
    except (AssertionError, Protocol0Error):
        pass

    kill_window_by_criteria(settings.ableton_process_name, search_type=SearchTypeEnum.PROGRAM_NAME)
    time.sleep(0.2)
    try:
        os.unlink(f"{settings.preferences_directory}\\CrashDetection.cfg")
        os.unlink(f"{settings.preferences_directory}\\CrashRecoveryInfo.cfg")
    except OSError:
        pass

    open_set("Test.als", confirm_dialog=False)


@limits(calls=1, period=5)
def open_set(filename: str, confirm_dialog=True):
    logger.info(f"opening {filename}")

    path_info = PathInfo.create(filename)

    relative_path = path_info.filename.replace(f"{settings.ableton_set_directory}\\", "").replace(
        "//", "\\"
    )
    notify(f"Opening '{relative_path}'")

    try:
        focus_ableton()
    except Protocol0Error:
        pass

    execute_powershell_command(f'& "{settings.ableton_exe}" "{path_info.filename}"', minimized=True)
    time.sleep(1.5)

    if confirm_dialog:
        for _ in range(3):
            send_right()
            send_keys("{ENTER}")
            time.sleep(0.5)


@keep_mouse_position
def save_set_as_template():
    if settings.is_ableton_11:
        notify("Not available in live 11", NotificationEnum.WARNING)
        return

    p0_script_client().dispatch(ResetPlaybackCommand())
    send_keys("^,")
    time.sleep(0.1)

    y_offset = 0
    if get_pixel_color_at((900, 185)) == PixelColorEnum.WHITE:
        y_offset = 30

    click((703, 333 + y_offset))  # click on File Folder
    click((1032, 195 + y_offset))  # click on set as new

    time.sleep(0.05)
    send_keys("{ENTER}")
    time.sleep(0.2)
    send_keys("	{ESC}")
    time.sleep(0.3)

    reload_ableton()


def toggle_fold_set():
    send_keys("{TAB}")
    send_keys("%u")
    time.sleep(0.01)
    send_keys("%u")
    send_keys("{TAB}")
