from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface


class InstrumentSynthMaster2(InstrumentInterface):
    NAME = "SynthMaster2"
    DEVICE = DeviceEnum.SYNTH_MASTER_2
