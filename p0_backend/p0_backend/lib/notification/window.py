from typing import Optional

# noinspection PyUnresolvedReferences
from PySimpleGUI import Window as SgWindow


class Window:
    sg_window: Optional[SgWindow] = None

    def display(self):
        raise NotImplementedError

    def is_event_escape(self, event: Optional[str]) -> bool:
        if event is None:
            return False

        return event == "Exit" or event == "__TIMEOUTS__" or event.split(":")[0] == "Escape"

    def is_event_enter(self, event: Optional[str]) -> bool:
        if event is None:
            return False

        return len(event) == 1 and ord(event) == 13
