from typing import List, Tuple

import PySimpleGUI as sg
from PySimpleGUI import Button
from protocol0.application.command.EmitBackendEventCommand import (
    EmitBackendEventCommand,
)
from p0_backend.api.client.p0_script_api_client import p0_script_client
from p0_backend.lib.notification.select.button_colors import ButtonColors
from p0_backend.lib.notification.window import Window
from p0_backend.lib.enum.color_enum import ColorEnum


class Select(Window):
    def __init__(
        self,
        message: str,
        options: List,
        buttons: List[List[Button]],
        arrow_keys: Tuple[str, str],
        background_color: ColorEnum,
        button_colors: ButtonColors,
    ):
        layout = [
            [sg.Text(message, key="question", background_color=background_color.hex_value)],
            [sg.Input(key="input", visible=False)],
            *buttons,
        ]
        self._arrow_keys = arrow_keys
        self._button_colors = button_colors

        self.sg_window = sg.Window(
            "Select Window",
            layout,
            modal=True,
            return_keyboard_events=True,
            keep_on_top=True,
            no_titlebar=True,
            element_justification="c",
            background_color=background_color.hex_value,
        )
        self._options = options
        self._selected_option = options[0]

    def display(self):
        self.focus()
        while True:
            event, values = self.sg_window.read()

            if self.is_event_escape(event) or self.is_event_enter(event):
                break

            if isinstance(event, str):
                key = event.split(":")[0]
                if key in self._arrow_keys:
                    self._scroll_selected_option(go_next=key == self._arrow_keys[1])
                elif event in self._options:
                    self._selected_option = event
                    break

        self.sg_window.close()

        p0_script_client().dispatch(
            EmitBackendEventCommand("option_selected", data=self._selected_option)
        )

    def _scroll_selected_option(self, go_next=True):
        increment = 1 if go_next else -1
        index = (self._options.index(self._selected_option) + increment) % len(self._options)
        self.sg_window[self._selected_option].update(
            button_color=("white", self._button_colors.default_color)
        )
        self._selected_option = self._options[index]
        self.sg_window[self._selected_option].update(
            button_color=("white", self._button_colors.selected_color)
        )
