from typing import Any, cast

import Live

from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device.Sample.Sample import Sample
from protocol0.domain.shared.scheduler.Scheduler import Scheduler


class SimplerDevice(Device):
    def __init__(self, *a: Any, **k: Any) -> None:
        super(SimplerDevice, self).__init__(*a, **k)
        self._device: Live.SimplerDevice.SimplerDevice = cast(
            Live.SimplerDevice.SimplerDevice, self._device
        )
        self._sample = Sample(self._device.sample)
        Scheduler.defer(self._set_warping)

    def __repr__(self) -> str:
        return "SimplerDevice(name=%s, sample=%s)" % (self.name, "test")

    @property
    def sample(self) -> Sample:
        return self._sample

    def _set_warping(self) -> None:
        if hasattr(self, "sample") and "loop" in self.sample.file_path.lower():
            self.sample.warping = True
            self._device.playback_mode = Live.SimplerDevice.PlaybackMode.classic
            release = self.get_parameter_by_name("Ve Release")
            release.value = 0.55  # 425 ms
