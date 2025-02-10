from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface
from protocol0.domain.lom.instrument.instrument.InstrumentParamEnum import InstrumentParamEnum
from protocol0.shared.Song import Song


class InstrumentSylenth1(InstrumentInterface):
    NAME = "Sylenth1"
    DEVICE = DeviceEnum.SYLENTH1
    PARAMETER_NAMES = {
        InstrumentParamEnum.DELAY: "Delay Dry/Wet",
        InstrumentParamEnum.FILTER: "FilterCtl Cutoff",
        InstrumentParamEnum.REVERB: "Reverb Dry/Wet",
        InstrumentParamEnum.VOLUME: "Main Volume",
    }

    def on_loaded(self, device_enum: DeviceEnum) -> None:
        Song.selected_track().arm_state.arm()
