import Live

from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.shared.ui.ColorEnum import ColorEnum


class AudioClip(Clip):
    @property
    def warping(self) -> bool:
        return self._clip.warping

    @warping.setter
    def warping(self, warping: bool) -> None:
        self._clip.warping = warping

    @property
    def warp_mode(self) -> Live.Clip.WarpMode:
        return self._clip.warp_mode

    @warp_mode.setter
    def warp_mode(self, warp_mode: Live.Clip.WarpMode) -> None:
        self._clip.warp_mode = warp_mode

    @property
    def file_path(self) -> str:
        return self._clip.file_path if self._clip else ""

    def focus(self) -> None:
        self.color = ColorEnum.FOCUSED.value
