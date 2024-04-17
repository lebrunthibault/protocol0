from functools import partial

from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.device_parameter.DeviceParamEnum import DeviceParamEnum
from protocol0.domain.lom.scene.Scene import Scene
from protocol0.domain.lom.scene.SceneLastBarPassedEvent import SceneLastBarPassedEvent
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.scheduler.BarChangedEvent import BarChangedEvent
from protocol0.domain.track_recorder.RecordProcessorInterface import RecordProcessorInterface
from protocol0.domain.track_recorder.config.RecordConfig import RecordConfig
from protocol0.shared.sequence.Sequence import Sequence


def _should_skip_scene(track: SimpleTrack, scene: Scene) -> bool:
    midi_note_track = track.input_routing.track
    cthulhu = midi_note_track.devices.get_one_from_enum(DeviceEnum.CTHULHU)

    cs = midi_note_track.clip_slots[scene.index]
    if cthulhu and not cs.clip:
        return True

    # checks if cthulhu and cthulhu clip is empty pattern
    cthulhu = midi_note_track.devices.get_one_from_enum(DeviceEnum.CTHULHU)
    if cthulhu:
        cthulhu_pattern = cthulhu.get_parameter_by_name(DeviceParamEnum.PATTERN)
        if cthulhu_pattern:
            pattern_env = cs.clip.automation.get_envelope(cthulhu_pattern)
            return pattern_env is not None and pattern_env.equals(cthulhu_pattern.max)

    return False


class RecordMidiNoteTrack(RecordProcessorInterface):
    def process(self, track: SimpleTrack, config: RecordConfig) -> Sequence:
        """Workaround for un precise timing : slow down the tempo on the end"""
        seq = Sequence()

        if not _should_skip_scene(track, config.recording_scene):
            seq.add(partial(config.clip_slots[0].prepare_for_record, clear=False))
            seq.add(config.recording_scene.fire)
            seq.log("scene fired")
            seq.add(config.clip_slots[0].fire)
            seq.wait_for_event(SceneLastBarPassedEvent)
            seq.log("last bar passed")
            seq.wait_beats(2)

        if config.recording_scene == config.recording_scene.next_scene:
            seq.wait_for_event(BarChangedEvent, continue_on_song_stop=True)
            return seq.done()

        config.scene_index = config.recording_scene.next_scene.index
        seq.add(partial(self.process, track, config))

        return seq.done()
