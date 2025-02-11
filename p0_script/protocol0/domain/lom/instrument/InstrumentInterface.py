from typing import Optional, Dict

from _Framework.SubjectSlot import SlotManager

from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.device.PluginDevice import PluginDevice
from protocol0.domain.lom.device.RackDevice import RackDevice
from protocol0.domain.lom.instrument.instrument.InstrumentParamEnum import InstrumentParamEnum


class InstrumentInterface(SlotManager):
    NAME = ""
    DEVICE: Optional[DeviceEnum] = None
    PARAMETER_NAMES: Dict[InstrumentParamEnum, str] = {}

    # noinspection PyInitNewSignature
    def __init__(self, device: Optional[Device], rack_device: Optional[RackDevice] = None) -> None:
        super(InstrumentInterface, self).__init__()
        self.device = device

    def __repr__(self) -> str:
        return self.__class__.__name__

    @property
    def name(self) -> str:
        if self.NAME:
            return self.NAME
        else:
            return self.device.name

    @property
    def full_name(self) -> str:
        full_name = self.device.name

        if (
            isinstance(self.device, PluginDevice)
            and self.device.selected_preset
            and self.device.selected_preset != "Default"
        ):
            full_name += f": {self.device.selected_preset}"

        return full_name

    def on_loaded(self, device_enum: DeviceEnum) -> None:
        return
