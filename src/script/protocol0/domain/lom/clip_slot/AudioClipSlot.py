from functools import partial
from typing import Any, Optional

from protocol0.domain.lom.clip.AudioClip import AudioClip
from protocol0.domain.lom.clip_slot.ClipSlot import ClipSlot
from protocol0.shared.sequence.Sequence import Sequence


class AudioClipSlot(ClipSlot):
    CLIP_CLASS = AudioClip

    def __init__(self, *a: Any, **k: Any) -> None:
        super(AudioClipSlot, self).__init__(*a, **k)
        self.clip: Optional[AudioClip] = self.clip

    def duplicate_clip_to(self, clip_slot: "AudioClipSlot") -> Sequence:
        seq = Sequence()
        seq.add(partial(super(AudioClipSlot, self).duplicate_clip_to, clip_slot))
        seq.add(clip_slot.notify_observers)
        return seq.done()
