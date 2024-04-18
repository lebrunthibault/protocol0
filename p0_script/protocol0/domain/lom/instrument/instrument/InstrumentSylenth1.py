from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.instrument.InstrumentColorEnum import InstrumentColorEnum
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface
from protocol0.domain.lom.instrument.instrument.InstrumentParamEnum import InstrumentParamEnum
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
    PARAMETER_NAMES = {
        InstrumentParamEnum.DELAY: "Delay Dry/Wet",
        InstrumentParamEnum.FILTER: "FilterCtl Cutoff",
        InstrumentParamEnum.REVERB: "Reverb Dry/Wet",
        InstrumentParamEnum.VOLUME: "Main Volume",
    }

    def on_loaded(self, device_enum: DeviceEnum) -> None:
        Song.selected_track().arm_state.arm()

        DomainEventBus.emit(PresetProgramSelectedEvent(96))

    def scroll_attack(self, go_next: bool) -> None:
        self.device.get_parameter_by_name("AmpEnv A Attack").scroll(go_next)
        self.device.get_parameter_by_name("ModEnv 1 Attack").scroll(go_next)
        self.device.get_parameter_by_name("AmpEnv B Attack").scroll(go_next)

    def scroll_decay(self, go_next: bool) -> None:
        self.device.get_parameter_by_name("AmpEnv A Decay").scroll(go_next)
        self.device.get_parameter_by_name("ModEnv 1 Decay").scroll(go_next)
        self.device.get_parameter_by_name("AmpEnv B Decay").scroll(go_next)

    def scroll_release(self, go_next: bool) -> None:
        self.device.get_parameter_by_name("AmpEnv A Release").scroll(go_next)
        self.device.get_parameter_by_name("ModEnv 1 Release").scroll(go_next)
        self.device.get_parameter_by_name("AmpEnv B Release").scroll(go_next)
