from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.shared.sequence.Sequence import Sequence


class BrowserServiceInterface(object):
    def load_device_from_enum(self, device_enum: DeviceEnum) -> Sequence:
        raise NotImplementedError

    def load_from_user_library(self, name: str) -> Sequence:
        raise NotImplementedError

    def load_sample(self, sample_name: str) -> Sequence:
        raise NotImplementedError

    def load_drum_pad_sample(self, sample_name: str) -> Sequence:
        raise NotImplementedError
