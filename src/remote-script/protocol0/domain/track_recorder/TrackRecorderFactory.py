from typing import Optional, List

from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.track_recorder.RecordTypeEnum import RecordTypeEnum
from protocol0.domain.track_recorder.RecordConfig import RecordConfig
from protocol0.shared.Song import Song


class TrackRecorderFactory(object):
    def get_record_config(
        self, tracks: List[SimpleTrack], record_type: RecordTypeEnum, recording_bar_length: int
    ) -> RecordConfig:
        return RecordConfig(
            record_type=record_type,
            tracks=tracks,
            scene_index=self._get_recording_scene_index(tracks),
            bar_length=self._get_recording_bar_length(record_type, recording_bar_length),
        )

    def _get_recording_scene_index(self, tracks: List[SimpleTrack]) -> Optional[int]:
        for i in range(Song.scenes().length):
            # don't use the first slot, reserved for live
            if i == 0:
                continue
            if all(track.clip_slots[i].clip is None for track in tracks):
                return i

        # overwriting the penultimate clip
        if Song.scenes().length >= 2:
            return Song.scenes().length - 2

        return None

    def _get_recording_bar_length(self, record_type: RecordTypeEnum, bar_length: int) -> int:
        if record_type == RecordTypeEnum.MIDI:
            return bar_length
        elif record_type == RecordTypeEnum.AUDIO:
            return 1000
        else:
            raise Protocol0Warning("Invalid record type")
