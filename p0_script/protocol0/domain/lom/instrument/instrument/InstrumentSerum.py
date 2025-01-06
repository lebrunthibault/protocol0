from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface
from protocol0.domain.lom.instrument.instrument.InstrumentParamEnum import InstrumentParamEnum
from protocol0.domain.lom.instrument.preset.preset_changer.SerumCCPresetChanger import (
    SerumCCPresetChanger,
)
from protocol0.shared.Song import Song


class InstrumentSerum(InstrumentInterface):
    NAME = "Serum"
    DEVICE = DeviceEnum.SERUM
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
