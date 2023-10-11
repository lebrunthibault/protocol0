from typing import Optional

from protocol0.domain.lom.device.Device import Device


class PresetChangerInterface(object):
    def __init__(self, device: Optional[Device]) -> None:
        self._device = device

    def scroll(self, go_next: bool) -> None:
        raise NotImplementedError
