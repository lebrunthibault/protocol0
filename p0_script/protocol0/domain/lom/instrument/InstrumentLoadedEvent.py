from protocol0.domain.lom.device.DeviceEnum import DeviceEnum


class InstrumentLoadedEvent(object):
    def __init__(self, device_enum: DeviceEnum):
        self.device_enum = device_enum
