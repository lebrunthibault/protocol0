from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.instrument.InstrumentColorEnum import InstrumentColorEnum
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface
from protocol0.domain.lom.instrument.preset.PresetProgramSelectedEvent import (
    PresetProgramSelectedEvent,
)
from protocol0.domain.lom.instrument.preset.preset_changer.ProgramChangePresetChanger import (
    ProgramChangePresetChanger,
)
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.shared.Song import Song


class InstrumentSylenth1(InstrumentInterface):
    NAME = "Sylenth1"
    DEVICE = DeviceEnum.SYLENTH1
    TRACK_COLOR = InstrumentColorEnum.REV2
    PRESET_CHANGER = ProgramChangePresetChanger

    def on_loaded(self, device_enum: DeviceEnum) -> None:
        Song.selected_track().arm_state.arm()

        if device_enum == DeviceEnum.SYLENTH1_BASS:
            DomainEventBus.emit(PresetProgramSelectedEvent(2))
        elif device_enum == DeviceEnum.SYLENTH1_KEYS:
            DomainEventBus.emit(PresetProgramSelectedEvent(32))
        elif device_enum == DeviceEnum.SYLENTH1_LEAD:
            DomainEventBus.emit(PresetProgramSelectedEvent(64))
        elif device_enum == DeviceEnum.SYLENTH1_PLUCK:
            DomainEventBus.emit(PresetProgramSelectedEvent(96))
        else:
            DomainEventBus.emit(PresetProgramSelectedEvent(96))
