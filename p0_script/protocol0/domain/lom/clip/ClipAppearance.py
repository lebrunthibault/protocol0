import Live

from protocol0.domain.lom.clip.ClipColorEnum import ClipColorEnum
from protocol0.domain.lom.clip.ClipName import ClipName


class ClipAppearance(object):
    def __init__(self, live_clip: Live.Clip.Clip, clip_name: ClipName, color: int) -> None:
        self._live_clip = live_clip
        self._clip_name = clip_name
        self._color = color

    @property
    def color(self) -> int:
        return self._live_clip.color_index if self._live_clip else 0

    @color.setter
    def color(self, color_index: int) -> None:
        if self._live_clip:
            self._live_clip.color_index = color_index  # noqa

    def refresh(self) -> None:
        self._clip_name._name_listener(force=True)
        if self.color != ClipColorEnum.AUDIO_UN_QUANTIZED.value:
            self.color = self._color
