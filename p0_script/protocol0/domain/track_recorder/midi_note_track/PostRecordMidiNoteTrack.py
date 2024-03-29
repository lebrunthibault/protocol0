from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.lom.track.simple_track.midi.SimpleMidiTrack import toggle_note_track_routing
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.track_recorder.RecordProcessorInterface import RecordProcessorInterface
from protocol0.domain.track_recorder.config.RecordConfig import RecordConfig
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger


class PostRecordMidiNoteTrack(RecordProcessorInterface):
    def process(self, track: SimpleTrack, config: RecordConfig) -> None:
        toggle_note_track_routing(track)

        def set_clips_length() -> None:
            for clip in track.clips:
                scene_length = Song.scenes()[clip.index].length

                if clip.length > scene_length:
                    clip.loop.end = clip.loop.end_marker = scene_length
                elif clip.length < scene_length:
                    Logger.error(f"Recording error : Clip length {clip}")

                clip.clip_name.update("")

        Scheduler.defer(set_clips_length)
