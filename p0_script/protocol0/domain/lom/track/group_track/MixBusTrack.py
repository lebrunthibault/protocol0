import Live
from _Framework.CompoundElement import subject_slot_group

from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.shared.Song import Song


class MixBusTrack(SimpleAudioTrack):
    TRACK_NAME = "Mix Bus"

    @classmethod
    def is_track_valid(cls, track: SimpleTrack) -> bool:
        return track.name.strip().lower() == cls.TRACK_NAME.lower()

    @subject_slot_group("has_clip")
    def _has_clip_listener(self, clip_slot: Live.ClipSlot.ClipSlot) -> None:
        """Resize clips to scene length"""
        clip = self.clip_slots[list(self._track.clip_slots).index(clip_slot)].clip

        if clip is None:
            return

        def set_clip_length() -> None:
            clip.loop.length = Song.scenes()[clip.index].length

        Scheduler.defer(set_clip_length)
