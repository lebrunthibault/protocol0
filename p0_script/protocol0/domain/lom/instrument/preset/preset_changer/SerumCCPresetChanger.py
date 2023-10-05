from protocol0.domain.lom.instrument.preset.PresetProgramScrolledEvent import \
    PresetProgramScrolledEvent
from protocol0.domain.lom.instrument.preset.preset_changer.PresetChangerInterface import (
    PresetChangerInterface,
)
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus


class SerumCCPresetChanger(PresetChangerInterface):
    _DECREMENT_CC = 54
    _INCREMENT_CC = 55

    def scroll(self, go_next: bool) -> None:
        cc_value = self._INCREMENT_CC if go_next else self._DECREMENT_CC
        DomainEventBus.emit(PresetProgramScrolledEvent(cc_value=cc_value))
