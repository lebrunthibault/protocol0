from functools import partial
from typing import Callable, List

from _Framework.ButtonElement import ButtonElement
from _Framework.InputControlElement import MIDI_CC_TYPE

from protocol0.application.ContainerInterface import ContainerInterface
from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface
from protocol0.domain.shared.utils.error import log_exceptions
from protocol0.shared.Song import Song


class ActionGroupLaunchKeyMini(ActionGroupInterface):
    """Maps the 8 LaunchKey Mini encoders (CC 21-28 ch.1) to the 8 macros of
    the instrument rack on the selected track.

    The LaunchKey Mini sends absolute CC values (0-127), so we bypass MultiEncoder
    (which expects relative 1/65 scroll values) and listen to ButtonElements
    directly, like TrackEncoder does.
    """

    CHANNEL = 1
    FIRST_CC = 21
    MACRO_COUNT = 8

    def __init__(self, container: ContainerInterface, component_guard: Callable) -> None:
        super(ActionGroupLaunchKeyMini, self).__init__(container, component_guard)
        self._buttons: List[ButtonElement] = []

    def configure(self) -> None:
        channel = self.CHANNEL - 1
        with self._component_guard():
            for i in range(self.MACRO_COUNT):
                button = ButtonElement(True, MIDI_CC_TYPE, channel, self.FIRST_CC + i)
                button.add_value_listener(partial(self._on_cc, i))
                self._buttons.append(button)

    @staticmethod
    @log_exceptions
    def _on_cc(macro_index: int, value: int) -> None:
        rack = Song.selected_track().instrument_rack_device
        if not rack:
            return

        # parameters[0] is "Device On", the 8 macros follow
        param_index = macro_index + 1
        if param_index >= len(rack.parameters):
            return

        param = rack.parameters[param_index]
        param.value = param.min + (value / 127.0) * (param.max - param.min)

    def _disconnect(self) -> None:
        super(ActionGroupLaunchKeyMini, self)._disconnect()
        for button in self._buttons:
            button.disconnect()
        self._buttons = []
