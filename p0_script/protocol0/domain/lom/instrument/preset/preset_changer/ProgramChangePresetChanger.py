from protocol0.domain.lom.device.PluginDevice import PluginDevice
from protocol0.domain.lom.instrument.preset.PresetProgramSelectedEvent import (
    PresetProgramSelectedEvent,
)
from protocol0.domain.lom.instrument.preset.preset_changer.PresetChangerInterface import (
    PresetChangerInterface,
)
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.utils.utils import clamp


class ProgramChangePresetChanger(PresetChangerInterface):
    def scroll(self, go_next: bool) -> None:
        assert isinstance(self._device, PluginDevice), "can only scroll plugin presets"
        next_index = int(clamp(self._device.selected_preset_index + (1 if go_next else -1), 0, 128))
        from protocol0.shared.logging.Logger import Logger
        Logger.dev(f"pc next index: {next_index}")
        DomainEventBus.emit(PresetProgramSelectedEvent(next_index))
