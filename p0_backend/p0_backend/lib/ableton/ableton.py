import os
import time

import keyboard
import win32gui  # noqa
from loguru import logger
from ratelimit import limits

from p0_backend.lib.ableton.ableton_set.ableton_set import PathInfo
from p0_backend.lib.errors.Protocol0Error import Protocol0Error
from p0_backend.lib.keys import send_keys
from p0_backend.lib.keys import send_right
from p0_backend.lib.notification import notify
from p0_backend.lib.process import execute_powershell_command, kill_window_by_criteria
from p0_backend.lib.window.find_window import find_window_handle_by_enum, SearchTypeEnum
from p0_backend.lib.window.window import (
    focus_window,
    get_focused_window_process_name,
)
from p0_backend.settings import Settings

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
    try:
        focus_ableton()
    except (AssertionError, Protocol0Error):
        pass

    logger.success(settings.ableton_process_name)
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


def toggle_fold_set():
    send_keys("{TAB}")
    send_keys("%u")
    time.sleep(0.01)
    send_keys("%u")
    send_keys("{TAB}")
