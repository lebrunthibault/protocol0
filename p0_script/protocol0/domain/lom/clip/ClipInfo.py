from functools import partial
from typing import TYPE_CHECKING, List, Dict, Optional

from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.lom.device_parameter.DeviceParameter import DeviceParameter
from protocol0.shared.Song import Song
from protocol0.shared.sequence.Sequence import Sequence

if TYPE_CHECKING:
    from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack


class ClipInfo(object):
    _DEBUG = False

    def __init__(
        self,
        clip: Clip,
        device_parameters: List[DeviceParameter],
        duplicate_clips: Optional[List[Clip]] = None,
    ) -> None:
        duplicate_clips = duplicate_clips or []

        self.index = clip.index
        self.name = clip.name
        self.hash = clip.get_hash(device_parameters)
        self._duplicate_indexes = [clip.index for clip in duplicate_clips]

    def __repr__(self) -> str:
        return "ClipInfo(name=%s,hash=%s,duplicates=%s)" % (
            self.name,
            self.hash,
            self._duplicate_indexes,
        )

    @classmethod
    def create_from_clips(
        cls,
        clips: List[Clip],
        device_parameters: List[DeviceParameter],
        clean_duplicates: bool = False,
    ) -> List["ClipInfo"]:
        unique_clips_by_hash: Dict[float, List[Clip]] = {}

        for clip in clips:
            clip_hash = clip.get_hash(device_parameters)
            unique_clips_by_hash[clip_hash] = unique_clips_by_hash.get(clip_hash, []) + [clip]

        clip_infos = [
            cls(clips[0], device_parameters, clips[1:]) for clips in unique_clips_by_hash.values()
        ]

        if clean_duplicates:
            for clips in unique_clips_by_hash.values():
                for clip in clips[1:]:
                    clip.delete()

        return clip_infos

    def get_clips(self, clips: List[Clip]) -> List[Clip]:
        clip_indexes = [self.index] + self._duplicate_indexes

        return [clip for clip in clips if clip.index in clip_indexes]

    @classmethod
    def restore_duplicate_clips(cls, clip_infos: List["ClipInfo"]) -> Sequence:
        seq = Sequence()
        for clip_info in clip_infos:
            seq.add(partial(clip_info.restore_duplicates, Song.selected_track()))

        return seq.done()

    def restore_duplicates(self, track: "SimpleTrack") -> Sequence:
        """Restore duplicates removed before flattening"""
        source_cs = track.clip_slots[self.index]

        assert source_cs.clip is not None, "restore duplicates : no clip at index %s" % self.index

        seq = Sequence()
        seq.add(
            [
                partial(source_cs.duplicate_clip_to, track.clip_slots[index])
                for index in self._duplicate_indexes
            ]
        )

        return seq.done()
