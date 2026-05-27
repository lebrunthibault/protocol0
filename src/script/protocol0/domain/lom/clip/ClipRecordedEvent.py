from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from protocol0.domain.lom.clip.Clip import Clip


class ClipRecordedEvent(object):
    def __init__(self, clip: "Clip") -> None:
        self.clip = clip
