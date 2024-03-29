from typing import Optional, Any

from protocol0.domain.lom.device_parameter.DeviceParamEnum import DeviceParamEnum
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.validation.ValidatorInterface import ValidatorInterface


class DeviceParameterValidator(ValidatorInterface):
    def __init__(
        self, device: Device, device_parameter_enum: DeviceParamEnum, expected_value: Any
    ) -> None:
        self._device = device
        self._device_parameter_enum = device_parameter_enum
        self._expected_value = expected_value

    def get_error_message(self) -> Optional[str]:
        if self.is_valid():
            return None
        return "Expected %s.%s to be %s" % (
            self._device,
            self._device_parameter_enum,
            self._expected_value,
        )

    def is_valid(self) -> bool:
        parameter = self._device.get_parameter_by_name(self._device_parameter_enum)
        if parameter is None:
            return False

        return parameter.value == self._expected_value

    def fix(self) -> None:
        parameter = self._device.get_parameter_by_name(self._device_parameter_enum)
        if parameter is None:
            raise Protocol0Error(
                "Parameter %s not found in %s" % (self._device_parameter_enum, self._device)
            )

        parameter.value = self._expected_value
