from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.track_recorder.config.RecordConfig import RecordConfig
from protocol0.domain.track_recorder.RecordTypeEnum import RecordTypeEnum
from protocol0.domain.track_recorder.config.RecordProcessors import RecordProcessors


class AbstractTrackRecorderFactory(object):
    def get_record_config(
        self, track: AbstractTrack, record_type: RecordTypeEnum, recording_bar_length: int
    ) -> RecordConfig:
        raise NotImplementedError

    def get_processors(self, record_type: RecordTypeEnum) -> RecordProcessors:
        raise NotImplementedError
