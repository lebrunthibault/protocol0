from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface


class InstrumentKick2(InstrumentInterface):
    NAME = "Kick 2"
    DEVICE = DeviceEnum.KICK_2
