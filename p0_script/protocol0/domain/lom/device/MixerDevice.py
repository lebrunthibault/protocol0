import Live
from _Framework.SubjectSlot import SlotManager
from typing import List, Dict, TYPE_CHECKING

from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.device_parameter.DeviceParamEnum import DeviceParamEnum
from protocol0.domain.lom.device_parameter.DeviceParameter import DeviceParameter
from protocol0.domain.shared.utils.utils import clamp

if TYPE_CHECKING:
    from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack


def update_parent_compressor_from_volume(track: "SimpleTrack", db_offset: float = 0) -> None:
    from protocol0.shared.logging.Logger import Logger

    Logger.dev(f"volume change ! {track.group_track}")

    if not track.group_track:
        return

    comp = track.group_track.devices.get_one_from_enum(DeviceEnum.SSL_COMP)
    from protocol0.shared.logging.Logger import Logger

    Logger.dev(comp)
    if not comp:
        return

    comp_threshold = comp.get_parameter_by_name(DeviceParamEnum.THRESH)

    comp_threshold.value = clamp((track.volume + 36 + db_offset) / 36, 0, 1)


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

    @property
    def is_default(self) -> bool:
        return all(param.value == param.default_value for param in self.parameters)
