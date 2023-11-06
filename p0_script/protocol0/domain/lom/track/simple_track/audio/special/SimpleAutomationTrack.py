import Live
from _Framework.CompoundElement import subject_slot_group

from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import (
    SimpleAudioTrack,
    resize_clip_to_scene_length,
)


class SimpleAutomationTrack(SimpleAudioTrack):
    TRACK_NAME = "Mix Bus"

    @subject_slot_group("has_clip")
    def _has_clip_listener(self, clip_slot: Live.ClipSlot.ClipSlot) -> None:
        """Resize clips to scene length"""
        super(SimpleAutomationTrack, self)._has_clip_listener(clip_slot)
        resize_clip_to_scene_length(self, clip_slot)
