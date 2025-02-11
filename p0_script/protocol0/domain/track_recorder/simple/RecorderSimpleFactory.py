from typing import Optional

from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.track_recorder.RecordTypeEnum import RecordTypeEnum
from protocol0.domain.track_recorder.config.RecordConfig import RecordConfig
from protocol0.domain.track_recorder.config.RecordProcessors import RecordProcessors
from protocol0.domain.track_recorder.simple.PostRecordSimple import PostRecordSimple
from protocol0.shared.Song import Song


class TrackRecorderSimpleFactory(object):
    def get_record_config(
        self, track: SimpleTrack, record_type: RecordTypeEnum, recording_bar_length: int
    ) -> RecordConfig:
        return RecordConfig(
            record_type=record_type,
            tracks=[track],
            scene_index=self._get_recording_scene_index(track),
            bar_length=self._get_recording_bar_length(record_type, recording_bar_length),
        )

    def _get_recording_scene_index(self, track: SimpleTrack) -> Optional[int]:
        for i in range(Song.selected_scene().index, len(Song.scenes())):
            if not track.clip_slots[i].clip:
                return i

        return None

    def _get_recording_bar_length(self, record_type: RecordTypeEnum, bar_length: int) -> int:
        if record_type == RecordTypeEnum.MIDI:
            return bar_length
        elif record_type in (RecordTypeEnum.AUDIO, RecordTypeEnum.MIDI_RESAMPLE):
            return Song.selected_scene().bar_length
        else:
            raise Protocol0Warning("Invalid record type")

    def get_processors(self, record_type: RecordTypeEnum) -> RecordProcessors:
        return RecordProcessors(post_record=PostRecordSimple())
