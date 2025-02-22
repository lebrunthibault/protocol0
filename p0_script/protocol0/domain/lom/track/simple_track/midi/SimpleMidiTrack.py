from typing import List, cast

from protocol0.domain.lom.clip.MidiClip import MidiClip
from protocol0.domain.lom.clip_slot.MidiClipSlot import MidiClipSlot
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack


class SimpleMidiTrack(SimpleTrack):
    CLIP_SLOT_CLASS = MidiClipSlot

    @property
    def clip_slots(self) -> List[MidiClipSlot]:
        return cast(List[MidiClipSlot], super(SimpleMidiTrack, self).clip_slots)

    @property
    def clips(self) -> List[MidiClip]:
        return super(SimpleMidiTrack, self).clips  # noqa
