from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface
from protocol0.domain.lom.instrument.instrument.InstrumentParamEnum import InstrumentParamEnum
from protocol0.shared.Song import Song


class InstrumentSerum(InstrumentInterface):
    NAME = "Serum"
    DEVICE = DeviceEnum.SERUM
    PARAMETER_NAMES = {
        InstrumentParamEnum.DELAY: "Dly_Wet",
        InstrumentParamEnum.FILTER: "Fil Cutoff",
        InstrumentParamEnum.REVERB: "Verb Wet",
        InstrumentParamEnum.VOLUME: "MasterVol",
    }

    def on_loaded(self, device_enum: DeviceEnum) -> None:
        track = Song.selected_track()
        track.arm_state.arm()
