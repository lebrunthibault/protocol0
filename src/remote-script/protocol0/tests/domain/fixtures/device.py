import Live
from _Framework.SubjectSlot import Subject
from typing import List

from protocol0.domain.lom.device_parameter.DeviceParamEnum import DeviceParamEnum
from protocol0.tests.domain.fixtures.device_parameter import AbletonDeviceParameter


class AbletonDeviceView(Subject):
    def __init__(self):
        self.is_collapsed = False
        self.selected_chain = None
        self.is_showing_chain_devices = False


class AbletonDevice(Subject, Live.Device.Device):
    """Inherits the Live stub class so Device._get_class isinstance dispatch works."""

    __subject_events__ = ("parameters",)

    def __init__(self, name: str) -> None:
        self._live_ptr = id(self)
        self.name = name
        self.view = AbletonDeviceView()
        self.parameters = [AbletonDeviceParameter(DeviceParamEnum.DEVICE_ON.parameter_name)]
        self.can_have_drum_pads = False
        self.can_have_chains = False
        self.class_display_name = ""
        self.class_name = ""
        self.type = 2  # audio_effect
        self.is_active = True


class AbletonDeviceChain(Subject, Live.Chain.Chain):
    def __init__(self, name: str = "Chain") -> None:
        self._live_ptr = id(self)
        self.name = name
        self.devices: List[AbletonDevice] = []

    def delete_device(self, index: int) -> None:
        self.devices = self.devices[:index] + self.devices[index + 1 :]


class AbletonRackDevice(AbletonDevice, Live.RackDevice.RackDevice):
    def __init__(self, name: str = "Rack") -> None:
        AbletonDevice.__init__(self, name)
        self.can_have_chains = True
        self.class_name = "AudioEffectGroupDevice"
        self.chains: List[AbletonDeviceChain] = []
        self.has_macro_mappings = False
        self.macros_mapped: List = []
