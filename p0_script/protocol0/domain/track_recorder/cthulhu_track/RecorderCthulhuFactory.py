from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.track_recorder.AbstractRecorderFactory import (
    AbstractTrackRecorderFactory,
)
from protocol0.domain.track_recorder.RecordTypeEnum import RecordTypeEnum
from protocol0.domain.track_recorder.config.RecordConfig import RecordConfig
from protocol0.domain.track_recorder.config.RecordProcessors import RecordProcessors
from protocol0.domain.track_recorder.cthulhu_track.OnRecordCancelledCthulhu import (
    OnRecordCancelledCthulhu,
)
from protocol0.domain.track_recorder.cthulhu_track.PostRecordCthulhu import PostRecordCthulhu
from protocol0.domain.track_recorder.cthulhu_track.PreRecordCthulhu import PreRecordCthulhu
from protocol0.domain.track_recorder.cthulhu_track.RecordCthulhu import RecordCthulhu
from protocol0.shared.Song import Song


class TrackRecorderCthulhuFactory(AbstractTrackRecorderFactory):
    def get_record_config(
        self, track: SimpleTrack, record_type: RecordTypeEnum, recording_bar_length: int
    ) -> RecordConfig:
        return RecordConfig(
            record_name=record_type.value,
            tracks=[track],
            scene_index=Song.selected_scene().index,
            bar_length=Song.selected_scene().bar_length,
            records_midi=True,
            solo_count_in=False,
            clear_clips=False,
        )

    def get_processors(self, record_type: RecordTypeEnum) -> RecordProcessors:
        return RecordProcessors(
            pre_record=PreRecordCthulhu(),
            post_record=PostRecordCthulhu(),
            record=RecordCthulhu(),
            on_record_cancelled=OnRecordCancelledCthulhu(),
        )
