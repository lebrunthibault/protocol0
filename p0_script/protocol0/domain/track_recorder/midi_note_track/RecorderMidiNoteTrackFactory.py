from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.track_recorder.AbstractRecorderFactory import (
    AbstractTrackRecorderFactory,
)
from protocol0.domain.track_recorder.RecordTypeEnum import RecordTypeEnum
from protocol0.domain.track_recorder.config.RecordConfig import RecordConfig
from protocol0.domain.track_recorder.config.RecordProcessors import RecordProcessors
from protocol0.domain.track_recorder.midi_note_track.PostRecordMidiNoteTrack import (
    PostRecordMidiNoteTrack,
)
from protocol0.domain.track_recorder.midi_note_track.PreRecordMidiNoteTrack import (
    PreRecordMidiNoteTrack,
)
from protocol0.domain.track_recorder.midi_note_track.RecordMidiNoteTrack import RecordMidiNoteTrack
from protocol0.shared.Song import Song


class TrackRecorderMidiNoteTrackFactory(AbstractTrackRecorderFactory):
    def get_record_config(
        self, track: SimpleTrack, record_type: RecordTypeEnum, recording_bar_length: int
    ) -> RecordConfig:
        return RecordConfig(
            record_type=record_type,
            tracks=[track],
            scene_index=Song.selected_scene().index,
            bar_length=Song.selected_scene().bar_length,
        )

    def get_processors(self, record_type: RecordTypeEnum) -> RecordProcessors:
        return RecordProcessors(
            pre_record=PreRecordMidiNoteTrack(),
            post_record=PostRecordMidiNoteTrack(),
            record=RecordMidiNoteTrack(),
        )
