from typing import List, cast, Any

import Live
from _Framework.CompoundElement import subject_slot_group

from protocol0.domain.lom.clip.AudioClip import AudioClip
from protocol0.domain.lom.clip_slot.AudioClipSlot import AudioClipSlot
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack


class SimpleAudioTrack(SimpleTrack):
    CLIP_SLOT_CLASS = AudioClipSlot

    def __init__(self, *a: Any, **k: Any) -> None:
        super(SimpleAudioTrack, self).__init__(*a, **k)
        self._has_clip_listener.replace_subjects(self._track.clip_slots)

    @property
    def clip_slots(self) -> List[AudioClipSlot]:
        return cast(List[AudioClipSlot], super(SimpleAudioTrack, self).clip_slots)

    @property
    def clips(self) -> List[AudioClip]:
        return super(SimpleAudioTrack, self).clips  # noqa

    @subject_slot_group("has_clip")
    def _has_clip_listener(self, clip_slot: Live.ClipSlot.ClipSlot) -> None:
        clip = self.clip_slots[list(self._track.clip_slots).index(clip_slot)].clip
        if not clip:
            return None
