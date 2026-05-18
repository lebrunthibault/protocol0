from typing import List, TYPE_CHECKING, Iterator

from protocol0.domain.lom.clip.Clip import Clip

if TYPE_CHECKING:
    from protocol0.domain.lom.track.simple_track.SimpleTrackClipSlots import SimpleTrackClipSlots


class SimpleTrackClips(object):
    def __init__(
        self,
        clip_slots: "SimpleTrackClipSlots",
    ) -> None:
        self._clip_slots = clip_slots

    def __iter__(self) -> Iterator[Clip]:
        return iter(self._clips)

    @property
    def _clips(self) -> List[Clip]:
        return [
            clip_slot.clip
            for clip_slot in list(self._clip_slots)
            if clip_slot.has_clip and clip_slot.clip
        ]
