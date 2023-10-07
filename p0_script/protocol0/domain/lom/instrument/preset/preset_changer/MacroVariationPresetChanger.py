from protocol0.domain.lom.instrument.preset.preset_changer.PresetChangerInterface import (
    PresetChangerInterface,
)


class MacroVariationPresetChanger(PresetChangerInterface):
    def scroll(self, go_next: bool) -> None:
        assert self._rack_device, "Rack device mandatory to scroll macro variations"
        if go_next:
            self._rack_device.increment_variation()
        else:
            self._rack_device.decrement_variation()
