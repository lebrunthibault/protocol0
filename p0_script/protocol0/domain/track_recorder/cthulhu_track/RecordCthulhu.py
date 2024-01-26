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
    cthulhu_track = track.input_routing.track

    cs = cthulhu_track.clip_slots[scene.index]
    if not cs.clip:
        return True

    # checks if cthulhu clip is empty pattern
    cthulhu = cthulhu_track.devices.get_one_from_enum(DeviceEnum.CTHULHU)
    assert cthulhu, "Could not find Cthulhu track"
    cthulhu_pattern = cthulhu.get_parameter_by_name(DeviceParamEnum.PATTERN)
    assert cthulhu_pattern, "Could not find Cthulhu pattern param"
    pattern_env = cs.clip.automation.get_envelope(cthulhu_pattern)
    from protocol0.shared.logging.Logger import Logger

    Logger.dev(
        (
            cs.clip.name,
            pattern_env.value_at_time(0),
            cthulhu_pattern.max,
            pattern_env.equals(cthulhu_pattern.max),
        )
    )

    return pattern_env.equals(cthulhu_pattern.max)


class RecordCthulhu(RecordProcessorInterface):
    def process(self, track: SimpleTrack, config: RecordConfig) -> Sequence:
        """Workaround for un precise timing : slow down the tempo on the end"""
        seq = Sequence()

        if not _should_skip_scene(track, config.recording_scene):
            seq.add(partial(config.clip_slots[0].prepare_for_record, clear=False))
            seq.add(config.recording_scene.fire)
            seq.add(config.clip_slots[0].fire)
            seq.wait_for_event(SceneLastBarPassedEvent)
            seq.wait_beats(2)

        if config.recording_scene == config.recording_scene.next_scene:
            return seq.wait_for_event(BarChangedEvent, continue_on_song_stop=True).done()

        config.scene_index = config.recording_scene.next_scene.index
        seq.add(partial(self.process, track, config))

        return seq.done()
