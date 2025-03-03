from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface
from protocol0.domain.lom.instrument.instrument.InstrumentParamEnum import InstrumentParamEnum


class InstrumentSerum(InstrumentInterface):
    NAME = "Serum"
    DEVICE = DeviceEnum.SERUM
    PARAMETER_NAMES = {
        InstrumentParamEnum.DELAY: "Dly_Wet",
        InstrumentParamEnum.FILTER: "Fil Cutoff",
        InstrumentParamEnum.REVERB: "Verb Wet",
        InstrumentParamEnum.VOLUME: "MasterVol",
    }
