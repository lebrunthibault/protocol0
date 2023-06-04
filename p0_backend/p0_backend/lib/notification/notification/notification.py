import time
from typing import Optional

# noinspection PyUnresolvedReferences
import PySimpleGUI as sg
import pyautogui
from PySimpleGUI import WIN_CLOSED
from loguru import logger

from p0_backend.settings import Settings
from p0_backend.lib.task_cache import TaskCache
from p0_backend.lib.notification.window import Window
from p0_backend.lib.enum.color_enum import ColorEnum
from p0_backend.lib.window.window import focus_window


class Notification(Window):
    _WINDOW_TITLE = "Notification message"

    def __init__(
        self,
        message: str,
        background_color: ColorEnum,
        centered: bool,
        timeout: float = 0,
        autofocus=True,
    ):
        background_color_hex = background_color.hex_value
        self._timeout = timeout
        self._autofocus = autofocus

        self._start_at = time.time()
        self._task_cache = TaskCache()

        kw = {}
        width_offset = (75 + 8 * len(message)) * Settings().display_resolution_factor

        if not centered:
            kw["location"] = (pyautogui.size()[0] - width_offset, 20)

        self.sg_window = sg.Window(
            self._WINDOW_TITLE,
            layout=[[sg.Text(f"  {message}  ", background_color=background_color_hex)]],
            return_keyboard_events=True,
            no_titlebar=True,
            use_default_focus=False,
            background_color=background_color_hex,
            keep_on_top=True,
            **kw,
        )

    def display(self, task_id: Optional[str] = None):
        focused = False
        while True:
            event, values = self.sg_window.read(timeout=10)
            if not focused and self._autofocus:
                focus_window(self._WINDOW_TITLE)
            focused = True

            if self.is_event_escape(event) or self.is_event_enter(event) or event == WIN_CLOSED:
                break
            if self._timeout and time.time() - self._start_at > self._timeout:
                logger.info(f"window timeout closing task {task_id}")
                break
            elif task_id is not None and task_id in self._task_cache.revoked_tasks():
                logger.warning(f"task {task_id} revoked: closing window")
                break

        if task_id is not None:
            self._task_cache.remove_revoked_task(task_id)

        self.sg_window.close()
