from typing import Optional

from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.instrument.preset.InstrumentPreset import InstrumentPreset


class PresetChangerInterface(object):
    def __init__(self, device: Optional[Device], preset_offset: int) -> None:
        self._device = device
        self._preset_offset = preset_offset

    def load(self, preset: InstrumentPreset) -> None:
        raise NotImplementedError
