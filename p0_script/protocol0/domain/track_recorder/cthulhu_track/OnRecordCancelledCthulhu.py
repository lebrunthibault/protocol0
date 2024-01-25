from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.track_recorder.RecordProcessorInterface import RecordProcessorInterface
from protocol0.domain.track_recorder.config.RecordConfig import RecordConfig
from protocol0.shared.Song import Song


class OnRecordCancelledCthulhu(RecordProcessorInterface):
    def process(self, track: SimpleTrack, config: RecordConfig) -> None:
        Song.set_tempo(config.original_tempo)
