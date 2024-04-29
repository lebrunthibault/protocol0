import subprocess
import sys

import psutil
import win32process
from loguru import logger
from psutil import Process, NoSuchProcess

from p0_backend.lib.errors.Protocol0Error import Protocol0Error
from p0_backend.lib.window.find_window import find_window_handle_by_enum, SearchTypeEnum
from p0_backend.settings import Settings
from p0_backend.lib.notification import notify

settings = Settings()


def execute_powershell_command(command: str, minimized=False):
    powershell_command_line = (
        f"'cmd /c start {'/min' if minimized else ''} powershell -Command {{ {command} }}'"
    )
    logger.info(powershell_command_line)
    subprocess.call(
        ["powershell.exe", "invoke-expression", powershell_command_line],
        stdout=sys.stdout,
        cwd=settings.project_directory,
    )


def _get_window_pid_by_criteria(
    name: str, search_type: SearchTypeEnum = SearchTypeEnum.WINDOW_TITLE
) -> int:
    handle = find_window_handle_by_enum(name=name, search_type=search_type)
    if handle == 0:
        return 0

    _, pid = win32process.GetWindowThreadProcessId(handle)
    logger.info(f"{name}: found pid {pid}")
    return pid


def kill_window_by_criteria(name: str, search_type: SearchTypeEnum = SearchTypeEnum.WINDOW_TITLE):
    while True:
        pid = _get_window_pid_by_criteria(name=name, search_type=search_type)
        if pid > 0:
            logger.info(f"killing window with pid {pid}")
            try:
                Process(pid=pid).terminate()
            except NoSuchProcess:
                return
        else:
            return


def get_ableton_pid() -> int:
    for proc in psutil.process_iter():
        if "Ableton Live" in proc.name():
            return proc.pid

    raise Protocol0Error("Ableton process not found")


def measure_cpu_usage(interval: float = 10) -> float:
    p = psutil.Process(get_ableton_pid())
    notify(f"Measuring cpu usage for the next {interval} seconds")

    return p.cpu_percent(interval=interval) / psutil.cpu_count()
