from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface
from protocol0.domain.lom.instrument.instrument.InstrumentParamEnum import InstrumentParamEnum


class InstrumentSylenth1(InstrumentInterface):
    NAME = "Sylenth1"
    DEVICE = DeviceEnum.SYLENTH1
    PARAMETER_NAMES = {
        InstrumentParamEnum.DELAY: "Delay Dry/Wet",
        InstrumentParamEnum.FILTER: "FilterCtl Cutoff",
        InstrumentParamEnum.REVERB: "Reverb Dry/Wet",
        InstrumentParamEnum.VOLUME: "Main Volume",
    }
