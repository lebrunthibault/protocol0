from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface


class InstrumentDiva(InstrumentInterface):
    NAME = "Diva"
    DEVICE = DeviceEnum.DIVA
