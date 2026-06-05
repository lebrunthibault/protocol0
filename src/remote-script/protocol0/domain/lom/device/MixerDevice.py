from typing import List, Dict

import Live
from _Framework.SubjectSlot import SlotManager

from protocol0.domain.lom.device_parameter.DeviceParameter import DeviceParameter


class MixerDevice(SlotManager):
    def __init__(self, live_mixer_device: Live.MixerDevice.MixerDevice) -> None:
        super(MixerDevice, self).__init__()

        self._sends = [DeviceParameter(parameter) for parameter in live_mixer_device.sends]
        self._volume = DeviceParameter(live_mixer_device.volume)
        self._pan = DeviceParameter(live_mixer_device.panning)

    def to_dict(self) -> Dict:
        return {"params": [p.value for p in self.parameters]}

    def update_from_dict(self, mixer_data: Dict) -> None:
        assert len(self.parameters) == len(mixer_data["params"]), "Cannot update mixer device"
        for param, value in zip(self.parameters, mixer_data["params"]):
            param.value = value

    @property
    def parameters(self) -> List[DeviceParameter]:
        return self._sends + [self._volume] + [self._pan]

    @property
    def sends(self) -> List[DeviceParameter]:
        return self._sends

    @property
    def volume(self) -> DeviceParameter:
        return self._volume

    def reset(self) -> None:
        for param in self.parameters:
            param.value = 0
