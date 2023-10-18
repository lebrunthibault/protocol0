from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.instrument.InstrumentColorEnum import InstrumentColorEnum
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface
from protocol0.domain.lom.instrument.instrument.InstrumentParamEnum import \
    InstrumentParamEnum
from protocol0.domain.lom.instrument.preset.preset_changer.SerumCCPresetChanger import (
    SerumCCPresetChanger,
)
from protocol0.shared.Song import Song


class InstrumentSerum(InstrumentInterface):
    NAME = "Serum"
    DEVICE = DeviceEnum.SERUM
    TRACK_COLOR = InstrumentColorEnum.SERUM
    PRESETS_PATH = (
        "C:\\Users\\thiba\\OneDrive\\Documents\\Xfer\\Serum Presets\\System\\ProgramChanges.txt"
    )
    PRESET_CHANGER = SerumCCPresetChanger
    PARAMETER_NAMES = {
        InstrumentParamEnum.DELAY: "Dly_Wet",
        InstrumentParamEnum.FILTER: "Fil Cutoff",
        InstrumentParamEnum.REVERB: "Verb Wet",
        InstrumentParamEnum.VOLUME: "MasterVol",
    }

    def on_loaded(self, device_enum: DeviceEnum) -> None:
        track = Song.selected_track()
        track.arm_state.arm()
        self.preset_list.scroll(go_next=True)
        self.preset_list.scroll(go_next=False)

    def scroll_attack(self, go_next: bool) -> None:
        self.device.get_parameter_by_name("Env1 Atk").scroll(go_next)
        self.device.get_parameter_by_name("Env2 Atk").scroll(go_next)

    def scroll_release(self, go_next: bool) -> None:
        self.device.get_parameter_by_name("Env1 Rel").scroll(go_next)
        self.device.get_parameter_by_name("Env2 Rel").scroll(go_next)
