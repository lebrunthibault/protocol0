from typing import List, Any, cast

import Live

from protocol0.domain.lom.device.Device import Device


class PluginDevice(Device):
    def __init__(self, *a: Any, **k: Any) -> None:
        super(PluginDevice, self).__init__(*a, **k)
        self._device: Live.PluginDevice.PluginDevice = cast(
            Live.PluginDevice.PluginDevice, self._device
        )

    @property
    def presets(self) -> List[str]:
        if not self._device:
            return []

        return [str(preset) for preset in list(self._device.presets) if not str(preset) == "empty"]

    @property
    def selected_preset_index(self) -> int:
        return self._device.selected_preset_index if self._device else 0

    @selected_preset_index.setter
    def selected_preset_index(self, selected_preset_index: int) -> None:
        if self._device:
            self._device.selected_preset_index = selected_preset_index

    @property
    def selected_preset(self) -> str:
        return self.presets[self.selected_preset_index]

    @property
    def type_name(self) -> str:
        return self.name
