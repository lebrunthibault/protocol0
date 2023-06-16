from typing import List, Optional

from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.instrument.preset.InstrumentPreset import InstrumentPreset


class PresetInitializerInterface(object):
    def __init__(self, device: Optional[Device], track_name: str) -> None:
        """Fetches the selected preset from the device or track"""
        self._device = device
        self._track_name = track_name

    def get_selected_preset(self, presets: List[InstrumentPreset]) -> Optional[InstrumentPreset]:
        raise NotImplementedError
