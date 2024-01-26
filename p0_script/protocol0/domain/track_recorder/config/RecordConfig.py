from typing import List, Optional

from protocol0.domain.lom.clip_slot.ClipSlot import ClipSlot
from protocol0.domain.lom.scene.Scene import Scene
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.shared.Song import Song


class RecordConfig(object):
    def __init__(
        self,
        record_name: str,
        tracks: List[SimpleTrack],
        scene_index: Optional[int],
        bar_length: int,
        records_midi: bool,
        solo_count_in: bool = True,
        clear_clips: bool = True,
    ) -> None:
        self.record_name = record_name
        self.tracks = tracks
        self._scene_index = scene_index
        self.bar_length = bar_length
        self.records_midi = records_midi
        self.solo_count_in = solo_count_in
        self.clear_clips = clear_clips
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
        # noinspection SpellCheckingInspection
        return (
            "RecordConfig(\nrecord_name=%s,\ntracks=%s,\nscene_index=%s,\nbar_length=%s\nrecords_midi=%s,\n"
            % (
                self.record_name,
                self.tracks,
                self.scene_index,
                self.bar_length,
                self.records_midi,
            )
        )
