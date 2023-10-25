from typing import Dict, Union

from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.device.DeviceEnumGroup import DeviceEnumGroup


def _serialize_device_enum(d: Union[DeviceEnum, DeviceEnumGroup]) -> Union[str, Dict]:
    if isinstance(d, DeviceEnum):
        return d.name
    else:
        return d.to_dict()


def get_favorite_device_names():
    return [list(map(_serialize_device_enum, row)) for row in DeviceEnum.favorites()]
