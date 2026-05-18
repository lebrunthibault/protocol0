from typing import Optional

from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.device_parameter.DeviceParamEnum import DeviceParamEnum
from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning


class MasterTrack(SimpleAudioTrack):
    IS_ACTIVE = False

    @property
    def muted(self) -> bool:
        return self.volume != 0

    @property
    def god_particle(self) -> Optional[Device]:
        return self.devices.get_one_from_enum(DeviceEnum.GOD_PARTICLE, all_devices=True)

    @property
    def adptr(self) -> Optional[Device]:
        return self.devices.get_one_from_enum(
            DeviceEnum.ADPTR_METRIC_AB, all_devices=True, enabled=True
        )

    def activate_adptr_filter(self, filter_type: str) -> None:
        if not self.adptr:
            raise Protocol0Warning("ADPTR not found")

        filter_switch = self.adptr.get_parameter_by_name(DeviceParamEnum.FILTER_SWITCH)

        if not filter_switch:
            raise Protocol0Warning("Filter Switch not mapped on ADPTR")

        filter_preset = self.adptr.get_parameter_by_name(DeviceParamEnum.FILTER_PRESET)
        if not filter_preset:
            raise Protocol0Warning("Filter Preset not mapped on ADPTR")

        filter_preset_to_value = {
            "sub": 0.6,
            "bass": 0.8,
            "low_mid": 0,
            "mid": 0.2,
            "high": 0.4,
        }

        filter_preset.value = filter_preset_to_value[filter_type]
