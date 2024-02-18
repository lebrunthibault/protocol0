from protocol0.domain.lom.clip.MidiClip import MidiClip
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.track_recorder.RecordProcessorInterface import RecordProcessorInterface
from protocol0.domain.track_recorder.config.RecordConfig import RecordConfig
from protocol0.shared.Song import Song


class PreRecordMidiNoteTrack(RecordProcessorInterface):
    def process(self, track: SimpleTrack, config: RecordConfig) -> None:
        if track.input_routing.track.devices.get_one_from_enum(DeviceEnum.CTHULHU):
            Song.set_tempo(500)

        for clip in track.clips:  # type: MidiClip
            if clip.index >= config.scene_index:
                clip.clear_notes()
