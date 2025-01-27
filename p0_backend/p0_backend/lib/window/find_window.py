import enum
from typing import Optional, Union

import win32api
import win32con
import win32gui
import win32process
from loguru import logger

from p0_backend.lib.errors.Protocol0Error import Protocol0Error


class SearchTypeEnum(enum.Enum):
    WINDOW_TITLE = "TITLE"
    PROGRAM_NAME = "PROGRAM_NAME"
    WINDOW_CLASS_NAME = "WINDOW_CLASS_NAME"


def find_window_handle_by_enum(
    name: str, search_type: Union[SearchTypeEnum, str] = SearchTypeEnum.WINDOW_TITLE
) -> int:
    logger.disable(__name__)
    if search_type == SearchTypeEnum.WINDOW_TITLE:
        handle = win32gui.FindWindow(None, name)
    elif search_type == SearchTypeEnum.PROGRAM_NAME:
        handle = _find_window_handle_by_criteria(app_name=name)
    elif search_type == SearchTypeEnum.WINDOW_CLASS_NAME:
        handle = _find_window_handle_by_criteria(class_name=name)
    else:
        raise Protocol0Error("Invalid enum value %s" % search_type)

    logger.enable(__name__)
    if not handle:
        logger.debug(f"{name} - {search_type} : Window handle not found {handle}")

    return handle


def _find_window_handle_by_criteria(
    class_name: Optional[str] = None, app_name: Optional[str] = None
) -> int:
    assert class_name or app_name, "You should give a criteria to search a message"

    handle = 0

    def win_enum_handler(hwnd: int, _):
        nonlocal handle
        handle_app_name = _get_app_name(hwnd)
        if handle_app_name == "chrome.exe":
            return

        if (
            win32gui.IsWindowVisible(hwnd)
            and (not class_name or win32gui.GetClassName(hwnd) == class_name)
            and (not app_name or handle_app_name == app_name)
        ):
            handle = hwnd

    win32gui.EnumWindows(win_enum_handler, None)

    return handle


def _get_app_name(handle: int) -> Optional[str]:
    """Get application base name given handle."""
    pid = win32process.GetWindowThreadProcessId(handle)
    try:
        logger.disable(__name__)  # silences warnings about protected processes
        handle = win32api.OpenProcess(
            win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False, pid[1]
        )
        logger.enable(__name__)
        return win32process.GetModuleFileNameEx(handle, 0).split("\\")[-1]
    except Exception as e:
        logger.error(e)
        return None
