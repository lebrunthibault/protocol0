import collections

from typing import Dict, Iterator, Any

from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.device.DrumRackDevice import DrumRackDevice
from protocol0.domain.lom.device.SimplerDevice import SimplerDevice
from protocol0.domain.shared.utils.list import find_if
from protocol0.shared.Song import Song


class DeviceStats(object):
    def __init__(self, name: str) -> None:
        self.count = 0
        self.device_enum = find_if(lambda enum: enum.class_name == name, list(DeviceEnum))
        self.name = self.device_enum.value if self.device_enum else name

    def __repr__(self) -> str:
        return "%s: %s => %sms" % (self.name, self.count, self.total_load_time)

    def increment(self) -> None:
        self.count += 1

    @property
    def total_load_time(self) -> int:
        load_time = self.device_enum.load_time if self.device_enum else 0
        return load_time * self.count


class DevicesStats(object):
    _EXCLUDED_DEVICE_NAMES = [
        DeviceEnum.EXTERNAL_AUDIO_EFFECT.value,
        DeviceEnum.SOUNDID_REFERENCE_PLUGIN.value,
        "Instrument Rack",
    ]

    def __init__(self) -> None:
        devices = list(self._get_devices())
        device_stats_dict: Dict[str, DeviceStats] = {}

        # group by name
        for device in devices:
            if device.type_name not in device_stats_dict:
                device_stats_dict[device.type_name] = DeviceStats(device.type_name)

            device_stats_dict[device.type_name].increment()

        devices_stats = list(device_stats_dict.values())
        devices_stats.sort(key=lambda x: x.total_load_time, reverse=True)

        self.count = len(devices)
        self.total_load_time = sum(stat.total_load_time for stat in device_stats_dict.values())
        self.device_stats = devices_stats
        self.kontakt_instances = len([d for d in devices if d.enum == DeviceEnum.KONTAKT])

    def _get_devices(self) -> Iterator[Device]:
        """Return only devices that matters for stats"""

        for track in Song.all_simple_tracks():
            for device in track.devices.all:
                if (
                    not isinstance(device, (SimplerDevice, DrumRackDevice))
                    and device.type_name not in self._EXCLUDED_DEVICE_NAMES
                ):
                    yield device

    def to_dict(self) -> Dict:
        output: Dict[str, Any] = collections.OrderedDict()
        output["count"] = self.count
        output["total load time"] = "%.2fs" % (float(self.total_load_time) / 1000)
        # output["top devices"] = [str(stat) for stat in self.device_stats[0:10]]
        output["kontakt instances"] = self.kontakt_instances

        return output
