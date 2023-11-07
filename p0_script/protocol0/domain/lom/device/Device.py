from typing import List, Any, Type, Optional, Union

import Live
from _Framework.SubjectSlot import SlotManager, subject_slot

from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.device_parameter.DeviceParamEnum import DeviceParamEnum
from protocol0.domain.lom.device_parameter.DeviceParameter import DeviceParameter
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.utils.list import find_if
from protocol0.domain.shared.utils.string import smart_string


class Device(SlotManager):
    def __init__(self, device: Live.Device.Device) -> None:
        super(Device, self).__init__()
        self._device = device
        self._view: Live.Device.Device.View = self._device.view
        self.parameters: List[DeviceParameter] = []
        self._parameters_listener.subject = self._device
        self._parameters_listener()
        self.can_have_drum_pads: bool = self._device.can_have_drum_pads
        self.can_have_chains: bool = self._device.can_have_chains

    def __repr__(self) -> str:
        return "%s(%s)" % (self.__class__.__name__, smart_string(self.name))

    @classmethod
    def _get_class(cls, device: Any) -> Type["Device"]:
        if isinstance(device, Live.RackDevice.RackDevice):
            from protocol0.domain.lom.device.RackDevice import RackDevice
            from protocol0.domain.lom.device.DrumRackDevice import DrumRackDevice

            if device.can_have_drum_pads:
                return DrumRackDevice
            else:
                return RackDevice
        elif isinstance(device, Live.PluginDevice.PluginDevice):
            from protocol0.domain.lom.device.PluginDevice import PluginDevice

            return PluginDevice
        elif isinstance(device, Live.SimplerDevice.SimplerDevice):
            from protocol0.domain.lom.device.SimplerDevice import SimplerDevice

            return SimplerDevice
        else:
            return Device

    @classmethod
    def make(cls, device: Live.Device.Device) -> "Device":
        return Device._get_class(device)(device=device)

    def on_added(self) -> None:
        pass

    @property
    def enum(self) -> Optional[DeviceEnum]:
        try:
            return DeviceEnum.from_value(self.name)
        except Protocol0Error:
            return None

    @subject_slot("parameters")
    def _parameters_listener(self) -> None:
        self.parameters = [
            DeviceParameter.create_from_name(self.name, parameter)
            for parameter in self._device.parameters
        ]

    def get_parameter_by_name(
        self, device_parameter_name: Union[DeviceParamEnum, str]
    ) -> Optional[DeviceParameter]:
        if isinstance(device_parameter_name, DeviceParamEnum):
            device_parameter_name = device_parameter_name.parameter_name
        return find_if(lambda p: p.name.lower() == device_parameter_name.lower(), self.parameters)

    @property
    def name(self) -> str:
        """Name of the device : user defined"""
        return self._device.name if self._device else ""

    @property
    def class_name(self) -> str:
        """type of the device for live devices else PluginDevice"""
        return self._device.class_name if self._device else ""

    @property
    def type_name(self) -> str:
        """type of the device (Reverb..) for Live or name of the plugin (FabFilter Pro-Q 3..)"""
        return self.class_name

    @property
    def is_instrument(self) -> bool:
        return self._device and self._device.type == Live.Device.DeviceType.instrument

    @property
    def is_midi(self) -> bool:
        return self._device and self._device.type == Live.Device.DeviceType.midi_effect

    @property
    def preset_name(self) -> Optional[str]:
        """overridden"""
        return None

    @property
    def is_enabled(self) -> bool:
        return self.get_parameter_by_name(DeviceParamEnum.DEVICE_ON).value == 1

    @is_enabled.setter
    def is_enabled(self, on: bool) -> None:
        self.get_parameter_by_name(DeviceParamEnum.DEVICE_ON).value = 1 if on else 0

    def toggle(self) -> None:
        self.is_enabled = not self.is_enabled

    @property
    def is_active(self) -> bool:
        """
        Return const access to whether this device is active.
        This will be false both when the device is off and when it's inside a rack device which is off.
        """
        return self._device.is_active

    @property
    def is_collapsed(self) -> bool:
        return self._view.is_collapsed

    @is_collapsed.setter
    def is_collapsed(self, is_collapsed: bool) -> None:
        self._view.is_collapsed = is_collapsed  # noqa
