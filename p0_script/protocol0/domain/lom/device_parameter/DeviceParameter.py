from typing import Any, Optional, List

import Live

from protocol0.domain.lom.device_parameter.DeviceParameterEnum import DeviceParameterEnum
from protocol0.domain.shared.ValueScroller import ValueScroller
from protocol0.domain.shared.utils.timing import accelerate, slow_down
from protocol0.domain.shared.utils.utils import clamp
from protocol0.shared.logging.Logger import Logger


class DeviceParameter(object):
    def __init__(
        self,
        device_parameter: Live.DeviceParameter.DeviceParameter,
        enum: Optional[DeviceParameterEnum] = None,
    ) -> None:
        self._device_parameter: Live.DeviceParameter.DeviceParameter = device_parameter
        self.device_name = ""

        try:
            if enum is not None:
                self.default_value = enum.default_value
            else:
                self.default_value = device_parameter.default_value
        except (RuntimeError, AttributeError):
            self.default_value = 0

    def __repr__(self, **k: Any) -> str:
        return "%s: %s" % (self.name, self.value)

    @classmethod
    def create_from_name(
        cls, device_name: str, device_parameter: Live.DeviceParameter.DeviceParameter
    ) -> "DeviceParameter":
        enum = DeviceParameterEnum.from_name(device_name, device_parameter.name)
        param = cls(device_parameter, enum=enum)
        param.device_name = device_name
        return param

    @property
    def name(self) -> str:
        if self._device_parameter:
            return self._device_parameter.name
        else:
            return ""

    @property
    def original_name(self) -> str:
        if self._device_parameter:
            return self._device_parameter.original_name
        else:
            return ""

    @property
    def value_items(self) -> List:
        if self._device_parameter:
            return self._device_parameter.value_items
        else:
            return []

    @property
    def value(self) -> float:
        if self._device_parameter:
            return self._device_parameter.value
        else:
            return 0

    @value.setter
    def value(self, value: float) -> None:
        if self.is_enabled and self._device_parameter:
            try:
                self._device_parameter.value = value
            except RuntimeError as e:
                Logger.warning(e)

    @property
    def automation_state(self) -> float:
        if self._device_parameter:
            return self._device_parameter.automation_state
        else:
            return 0

    @property
    def is_automated(self) -> bool:
        return self.automation_state != Live.DeviceParameter.AutomationState.none

    @property
    def min(self) -> float:
        if self._device_parameter:
            return self._device_parameter.min
        else:
            return 0

    @property
    def max(self) -> float:
        if self._device_parameter:
            return self._device_parameter.max
        else:
            return 0

    @property
    def is_quantized(self) -> bool:
        if self._device_parameter:
            return self._device_parameter.is_quantized
        else:
            return False

    @property
    def is_enabled(self) -> bool:
        if self._device_parameter:
            return self._device_parameter.is_enabled
        else:
            return False

    @classmethod
    def set_live_device_parameter(
        cls, param: Live.DeviceParameter.DeviceParameter, value: float
    ) -> None:
        if not param or not param.is_enabled:
            return None
        value = max(param.min, value)
        value = min(param.max, value)
        # noinspection PyPropertyAccess
        param.value = value

    @slow_down(factor=3)
    def scroll_slowed(self, go_next: bool, value_items: List = None) -> None:
        self.scroll(go_next, value_items)

    @accelerate
    def scroll(
        self, go_next: bool, value_items: List = None, factor: int = 1, steps: int = 1000
    ) -> None:
        if self.is_quantized:
            if value_items is None:
                value_items = list(self.value_items)

            self.value = ValueScroller.scroll_values(value_items, self.value, go_next, rotate=False)
            return

        # using factor acceleration
        value_range = self.max - self.min
        step = value_range / steps
        step *= factor  # used by accelerate decorator
        value = self.value + step if go_next else self.value - step
        self.value = clamp(value, self.min, self.max)

    def toggle(self) -> None:
        if self.value == self.min:
            self.value = self.max
        else:
            self.value = self.min

    def reset(self) -> None:
        if self.name == "Device On":
            # we define arbitrarily that toggling a device always starts from disabled state
            # not the opposite
            self.value = 0
        else:
            try:
                self.value = self.default_value
            except RuntimeError as e:
                Logger.error((e, self, self.device_name, self.min, self.max, self.default_value))
                raise e
