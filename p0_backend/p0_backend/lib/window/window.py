import ctypes
import tkinter
from typing import Union

import psutil
import pythoncom
import win32com.client
import win32gui  # noqa
import win32process
from loguru import logger
from psutil import NoSuchProcess

from p0_backend.lib.errors.Protocol0Error import Protocol0Error
from p0_backend.lib.window.find_window import SearchTypeEnum, find_window_handle_by_enum


def focus_window(
    name: str,
    search_type: Union[SearchTypeEnum, str] = SearchTypeEnum.WINDOW_TITLE,
) -> int:
    """

    Returns
    -------
    object
    """
    handle = find_window_handle_by_enum(name=name, search_type=search_type)
    if not handle:
        raise Protocol0Error(f"No window '{name}'")
    focus_window_by_handle(handle)

    return handle


def focus_window_by_handle(
    handle: int,
    retry: bool = True,
) -> int:
    # noinspection PyUnresolvedReferences
    pythoncom.CoInitialize()  # needed
    # noinspection PyBroadException
    try:
        win32gui.SetForegroundWindow(handle)
        return handle
    except Exception as e:
        logger.warning(f"couldn't focus {handle} : {e}")
        if retry:
            # needed for SetForegroundWindow to be allowed
            shell = win32com.client.Dispatch("WScript.Shell")
            shell.SendKeys("%")
            return focus_window_by_handle(handle, retry=False)

    logger.error(f"Window not focused : {handle}")
    raise Protocol0Error("window is not focused")


def focus_tkinter_window(root: tkinter.Tk):
    set_to_foreground = ctypes.windll.user32.SetForegroundWindow
    keyboard_event = ctypes.windll.user32.keybd_event
    alt_key = 0x12
    extended_key = 0x0001
    key_up = 0x0002

    keyboard_event(alt_key, 0, extended_key | 0, 0)
    set_to_foreground(root.winfo_id())
    keyboard_event(alt_key, 0, extended_key | key_up, 0)


def get_focused_window_process_name():
    res = win32process.GetWindowThreadProcessId(win32gui.GetForegroundWindow())
    pid = res[-1]
    if pid < 0:
        logger.warning(f"Got pid {pid}")
        return ""

    try:
        return psutil.Process(pid).name()
    except NoSuchProcess:
        return ""


def get_focused_window_title() -> str:
    return win32gui.GetWindowText(win32gui.GetForegroundWindow())
