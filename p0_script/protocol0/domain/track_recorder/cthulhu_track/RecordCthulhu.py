from functools import partial
from typing import Optional

from protocol0.domain.lom.scene.SceneLastBarPassedEvent import SceneLastBarPassedEvent
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.scheduler.BarChangedEvent import BarChangedEvent
from protocol0.domain.track_recorder.RecordProcessorInterface import RecordProcessorInterface
from protocol0.domain.track_recorder.config.RecordConfig import RecordConfig
from protocol0.shared.Song import Song
from protocol0.shared.sequence.Sequence import Sequence


class RecordCthulhu(RecordProcessorInterface):
    def process(self, track: SimpleTrack, config: RecordConfig) -> Sequence:
        """Workaround for un precise timing : slow down the tempo on the end"""
        config.clip_slots[0].fire()
        seq = Sequence()

        seq.wait_for_event(SceneLastBarPassedEvent)
        seq.wait_beats(2)

        seq.add(partial(self._launch_record_on_next_scene, track, config))
        return seq.done()

    def _launch_record_on_next_scene(
        self, track: SimpleTrack, config: RecordConfig
    ) -> Optional[Sequence]:
        next_scene = config.recording_scene.next_scene

        # No next scene or no midi clip on next scene -> recording stops
        if (
            next_scene == config.recording_scene
            or not track.input_routing.track.clip_slots[next_scene.index].clip
        ):
            Song.set_tempo(500)
            return Sequence().wait_for_event(BarChangedEvent).done()
            # Scheduler.wait_bars(config.bar_length - 3, partial(Song.set_tempo, 500))

        # pass to the next scene
        config.scene_index = next_scene.index
        seq = Sequence()
        seq.add(partial(config.clip_slots[0].prepare_for_record, clear=False))
        seq.add(config.recording_scene.fire)
        seq.add(partial(self.process, track, config))

        return seq.done()
