from protocol0.domain.lom.clip.MidiClip import MidiClip
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.track_recorder.RecordProcessorInterface import RecordProcessorInterface
from protocol0.domain.track_recorder.config.RecordConfig import RecordConfig


class PreRecordCthulhu(RecordProcessorInterface):
    def process(self, track: SimpleTrack, config: RecordConfig) -> None:
        for clip in track.clips:  # type: MidiClip
            if clip.index >= config.scene_index:
                clip.clear_notes()
