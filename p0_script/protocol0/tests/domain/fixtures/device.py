from _Framework.SubjectSlot import Subject

from protocol0.domain.lom.device_parameter.DeviceParamEnum import DeviceParamEnum
from protocol0.tests.domain.fixtures.device_parameter import AbletonDeviceParameter


class AbletonDevice(Subject):
    __subject_events__ = ("parameters",)

    def __init__(self, name: str) -> None:
        self._live_ptr = id(self)
        self.name = name
        self.view = None
        self.parameters = [AbletonDeviceParameter(DeviceParamEnum.DEVICE_ON.parameter_name)]
        self.can_have_drum_pads = False
        self.can_have_chains = False
        self.class_display_name = ""
