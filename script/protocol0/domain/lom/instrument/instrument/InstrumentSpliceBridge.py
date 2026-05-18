from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface


class InstrumentSpliceBridge(InstrumentInterface):
    NAME = "Splice"
    DEVICE = DeviceEnum.SPLICE_BRIDGE
