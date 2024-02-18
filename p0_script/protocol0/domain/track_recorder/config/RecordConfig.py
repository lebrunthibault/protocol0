from typing import List, Optional

from protocol0.domain.lom.clip_slot.ClipSlot import ClipSlot
from protocol0.domain.lom.scene.Scene import Scene
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.track_recorder.RecordTypeEnum import RecordTypeEnum
from protocol0.shared.Song import Song


class RecordConfig(object):
    def __init__(
        self,
        record_type: RecordTypeEnum,
        tracks: List[SimpleTrack],
        scene_index: Optional[int],
        bar_length: int,
    ) -> None:
        self.record_type = record_type
        self.tracks = tracks
        self._scene_index = scene_index
        self.bar_length = bar_length

        self.original_tempo = Song.tempo()

    @property
    def scene_index(self) -> int:
        assert self._scene_index is not None, "No recording scene index"
        return self._scene_index

    @scene_index.setter
    def scene_index(self, scene_index: int) -> None:
        self._scene_index = scene_index

    @property
    def recording_scene(self) -> Scene:
        return Song.scenes()[self.scene_index]

    @property
    def clip_slots(self) -> List[ClipSlot]:
        return [track.clip_slots[self.scene_index] for track in self.tracks]

    def __repr__(self) -> str:
        return f"RecordConfig(\nrecord_type={self.record_type},\nscene={self.recording_scene},\nbar_length={self.bar_length}\n"
