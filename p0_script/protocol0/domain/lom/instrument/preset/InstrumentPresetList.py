from typing import List, Optional, Any

from protocol0.domain.lom.device.RackDevice import RackDevice
from protocol0.domain.lom.instrument.preset.InstrumentPreset import InstrumentPreset
from protocol0.domain.lom.instrument.preset.preset_changer.PresetChangerInterface import (
    PresetChangerInterface,
)
from protocol0.domain.lom.instrument.preset.preset_importer.PresetImportInterface import (
    PresetImportInterface,
)
from protocol0.domain.lom.instrument.preset.preset_initializer.PresetInitializerInterface import (
    PresetInitializerInterface,
)
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning


class InstrumentPresetList(object):
    def __init__(
        self,
        preset_importer: PresetImportInterface,
        preset_initializer: PresetInitializerInterface,
        preset_changer: PresetChangerInterface,
        rack_device: Optional[RackDevice],
    ) -> None:
        self._preset_importer = preset_importer
        self._preset_initializer = preset_initializer
        self._preset_changer = preset_changer
        self._rack_device = rack_device
        self.presets: List[InstrumentPreset] = []
        self.selected_preset: Optional[InstrumentPreset] = None
        self.sync_presets()

    def __repr__(self, **k: Any) -> str:
        return "preset count: %d, selected preset: %s" % (len(self.presets), self.selected_preset)

    def sync_presets(self) -> None:
        self.presets = self._preset_importer.import_presets()
        self.selected_preset = self._preset_initializer.get_selected_preset(self.presets)

    @property
    def categories(self) -> List[str]:
        """overridden"""
        return sorted(
            list(
                set(
                    [
                        preset.category
                        for preset in self.presets
                        if preset.category and not preset.category.startswith("_")
                    ]
                )
            )
        )

    @property
    def selected_category(self) -> str:
        if self.selected_preset:
            return self.selected_preset.category
        else:
            return ""

    def set_selected_category(self, selected_category: Optional[str]) -> None:
        presets = self._category_presets(selected_category)
        if len(presets) == 0:
            raise Protocol0Warning("Cannot find presets in category '%s'" % selected_category)

        self.selected_preset = presets[0]

    def _category_presets(self, category: Optional[str] = None) -> List[InstrumentPreset]:
        return list(
            filter(lambda p: p.category == (category or self.selected_category), self.presets)
        )

    def scroll(self, go_next: bool) -> None:
        # macro variations have precedence o
        if self._rack_device and self._rack_device.variation_count > 0:
            if go_next:
                self._rack_device.increment_variation()
            else:
                self._rack_device.decrement_variation()
            return

        self._preset_changer.scroll(go_next)
