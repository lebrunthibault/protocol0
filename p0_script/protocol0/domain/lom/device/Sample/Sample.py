import os

import Live

from protocol0.domain.shared.utils.string import smart_string


class Sample(object):
    def __init__(self, sample: Live.Sample.Sample) -> None:
        self._sample = sample

    def __repr__(self) -> str:
        return "Sample(name='%s')" % self.name

    @property
    def name(self) -> str:
        return str(os.path.splitext(os.path.basename(smart_string(self.file_path)))[0])

    @property
    def length(self) -> float:
        return self._sample.length

    @property
    def file_path(self) -> str:
        if self._sample:
            return self._sample.file_path
        else:
            return ""

    @property
    def warping(self) -> bool:
        return self._sample.warping

    @warping.setter
    def warping(self, warping: bool) -> None:
        self._sample.warping = warping

    @property
    def warp_mode(self) -> Live.Clip.WarpMode:
        return self._sample.warp_mode

    @warp_mode.setter
    def warp_mode(self, warp_mode: Live.Clip.WarpMode) -> None:
        self._sample.warp_mode = warp_mode

    def beat_to_sample_time(self, beat_time: float) -> float:
        return self._sample.beat_to_sample_time(beat_time)
