from typing import List

from protocol0.domain.lom.device.PluginDevice import PluginDevice
from protocol0.domain.lom.instrument.preset.InstrumentPreset import InstrumentPreset
from protocol0.domain.lom.instrument.preset.preset_importer.PresetImportInterface import (
    PresetImportInterface,
)


class PluginDevicePresetImporter(PresetImportInterface):
    def __init__(self, device: PluginDevice) -> None:
        self._device = device

    def _import_presets(self) -> List[InstrumentPreset]:
        return [
            InstrumentPreset(index=i, name=preset)
            for i, preset in enumerate(self._device.presets[0:128])
        ]
