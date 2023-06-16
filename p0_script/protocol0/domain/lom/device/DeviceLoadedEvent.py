from protocol0.domain.lom.device.DeviceEnum import DeviceEnum


class DeviceLoadedEvent(object):
    def __init__(self, device_enum: DeviceEnum) -> None:
        self.device_enum = device_enum
