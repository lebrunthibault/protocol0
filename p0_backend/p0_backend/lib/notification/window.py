from functools import partial
from typing import Optional

# noinspection PyUnresolvedReferences
from PySimpleGUI import Window as SgWindow

from p0_backend.lib.timer import start_timer
from p0_backend.lib.window.window import focus_window


class Window:
    sg_window: Optional[SgWindow] = None

    def display(self):
        raise NotImplementedError

    def focus(self):
        if self.sg_window.Title is None:
            return
        for interval in (0.5, 1):
            start_timer(interval, partial(focus_window, self.sg_window.Title))

    def is_event_escape(self, event: Optional[str]) -> bool:
        if event is None:
            return False

        return event == "Exit" or event == "__TIMEOUTS__" or event.split(":")[0] == "Escape"

    def is_event_enter(self, event: Optional[str]) -> bool:
        if event is None:
            return False

        return len(event) == 1 and ord(event) == 13
