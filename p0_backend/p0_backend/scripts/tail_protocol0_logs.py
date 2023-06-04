import ctypes
import re
import sys
import time
from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, TextIO

import click
import win32con
import win32gui
from loguru import logger
from rx import operators as op, create

from p0_backend.api.settings import Settings
from p0_backend.lib.console import clear_console
from p0_backend.lib.decorators import log_exceptions
from p0_backend.lib.process import kill_window_by_criteria
from p0_backend.lib.rx import rx_error, rx_nop
from p0_backend.lib.utils import log_string
from p0_backend.lib.window.find_window import SearchTypeEnum

settings = Settings()

logger = logger.opt(colors=True)
logger.remove()
logger.add(sys.stdout, format="<light-yellow>{time:HH:mm:ss.SSS}</> {message}")


class LogLevelEnum(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"


class LogConfig:
    PROCESS_LOGS = True
    START_SIZE = 300
    LOG_LEVEL = LogLevelEnum.DEBUG
    COLOR_SCHEME = {
        "light-yellow": ["P0 - dev"],
        "light-blue": ["P0 - notice"],
        "cyan": ["P0 - warning"],
        "green": ["P0 - info", "Protocol0", "P0"],
    }
    BLACK_LIST_KEYWORDS = [
        "silent exception thrown",
        "Midi(Out|In)Device",
        "MidiRemoteScript",
        "Python: INFO:_Framework.ControlSurface:",
        "INFO:transitions.core",
    ]
    FILTER_KEYWORDS = ["P0", "Protocol0"]
    ERROR_NON_KEYWORDS = [
        "\.wav. could not be opened",
        "traceback.format_stack",
        "Link: Disabled",
        "Push2.push2",
        "MemoryUsage:",
        "VST 2.4",
        "is an invalid filename",
    ]
    ERROR_KEYWORDS = [
        "P0 - error",
        "traceback",
        "RemoteScriptError",
        "ArgumentError",
        "exception",
        "VST3 presets with unknown device type found",
    ]
    CLEAR_KEYWORD = "clear_logs"
    PATTERNS_TO_REMOVE = [
        "P0 - (\\w+:)?",
        "Python: INFO:root:\\d* - ",
        "(info|debug):\\s?",
        "RemoteScriptError: ",
        "RemoteScriptMessage: ",
        "\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}.\\d{6}\\:",
    ]


class ErrorState:
    LAST_ERROR_STARTED_AT: Optional[float] = None

    @classmethod
    def in_error(cls):
        return (
            cls.LAST_ERROR_STARTED_AT is not None and time.time() - cls.LAST_ERROR_STARTED_AT > 0.01
        )

    @classmethod
    def reset(cls):
        cls.LAST_ERROR_STARTED_AT = None


@dataclass(frozen=True)
class LogLine:
    line: str
    color: Optional[str] = None
    is_error: bool = False

    def __str__(self):
        color = "red" if self.is_error else (self.color or "white")
        line = re.sub("\\\\$", "", self.line)  # remove trailing slash that crashes loguru
        return f"<{color}>{line}</{color}>"

    def has_patterns(self, patterns: List[str]):
        return any(re.search(pattern.lower(), self.line.lower()) for pattern in patterns)


def _get_clean_line(line: str) -> str:
    for pattern in LogConfig.PATTERNS_TO_REMOVE:
        line = re.sub(pattern, "", line)

    return line[2:] if line.startswith("  ") else line


def _filter_line(line: LogLine) -> bool:
    if line.has_patterns(LogConfig.BLACK_LIST_KEYWORDS):
        return False

    if line.is_error:
        return True

    if line.has_patterns([LogConfig.CLEAR_KEYWORD]):
        clear_console()
        return False

    return line.has_patterns(LogConfig.FILTER_KEYWORDS)


def _is_error(line: LogLine) -> bool:
    if line.has_patterns(LogConfig.ERROR_KEYWORDS) and not line.has_patterns(
        LogConfig.ERROR_NON_KEYWORDS
    ):
        ErrorState.LAST_ERROR_STARTED_AT = time.time()
        return True

    if not _get_clean_line(line.line).startswith(" ") or line.has_patterns(
        LogConfig.ERROR_NON_KEYWORDS
    ):
        ErrorState.reset()
        return False

    return ErrorState.in_error()


def _get_color(line: LogLine) -> Optional[str]:
    for color, sub_strings in LogConfig.COLOR_SCHEME.items():
        if line.has_patterns(sub_strings):
            return color
    return None


def get_line_observable_from_file(file: TextIO):
    sleep_sec = 0.1

    def _make_observable(observer, _):
        """Yield each line from a file as they are written.
        `sleep_sec` is the time to sleep after empty reads."""
        line = ""
        for line in file.readlines()[-LogConfig.START_SIZE :]:
            observer.on_next(line)

        while True:
            tmp = file.readline()
            if tmp is not None:
                line += tmp
                if line.endswith("\n"):
                    observer.on_next(line)
                    line = ""
            elif sleep_sec:
                time.sleep(sleep_sec)

    # noinspection PyTypeChecker
    return create(_make_observable)


@click.command()
@click.option("--raw", is_flag=True)
@log_exceptions
def tail_ableton_log_file(raw: bool):
    if raw:
        LogConfig.PROCESS_LOGS = False
        LogConfig.START_SIZE = 200

    kill_window_by_criteria(name=settings.log_window_title, search_type=SearchTypeEnum.WINDOW_TITLE)

    win32gui.ShowWindow(win32gui.GetForegroundWindow(), win32con.SHOW_FULLSCREEN)
    ctypes.windll.kernel32.SetConsoleTitleW(settings.log_window_title)

    if LogConfig.LOG_LEVEL == LogLevelEnum.INFO:
        LogConfig.BLACK_LIST_KEYWORDS.append("P0 - debug")

    pipes = [
        op.map(lambda line: line.replace("\n", "")),
        op.map(log_string),
    ]

    if LogConfig.PROCESS_LOGS:
        pipes += [
            op.map(lambda line: LogLine(line=line)),
            op.map(lambda line: LogLine(line=line.line, is_error=_is_error(line))),
            op.filter(_filter_line),
            op.map(
                lambda line: LogLine(line=line.line, is_error=line.is_error, color=_get_color(line))
            ),
            op.map(
                lambda line: LogLine(
                    line=_get_clean_line(line.line), is_error=line.is_error, color=line.color
                )
            ),
        ]

    with open(settings.log_file, "r") as file:
        log_obs = get_line_observable_from_file(file)
        log_obs.pipe(*pipes).subscribe(logger.info, rx_error)
        log_obs.pipe(*pipes).subscribe(rx_nop, logger.error)
