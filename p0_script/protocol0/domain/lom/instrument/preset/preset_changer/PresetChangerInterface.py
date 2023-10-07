from typing import Optional

from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device.RackDevice import RackDevice


class PresetChangerInterface(object):
    def __init__(self, device: Optional[Device], rack_device: Optional[RackDevice]) -> None:
        self._device = device
        self._rack_device = rack_device

    def scroll(self, go_next: bool) -> None:
        raise NotImplementedError
