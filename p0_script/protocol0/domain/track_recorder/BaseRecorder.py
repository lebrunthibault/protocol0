from functools import partial
from typing import cast, List

from protocol0.domain.lom.song.SongStartedEvent import SongStartedEvent
from protocol0.domain.lom.song.SongStoppedEvent import SongStoppedEvent
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.scheduler.BarChangedEvent import BarChangedEvent
from protocol0.domain.track_recorder.RecordConfig import RecordConfig
from protocol0.shared.Song import Song
from protocol0.shared.sequence.Sequence import Sequence


def record_from_config(config: RecordConfig) -> Sequence:
    # launch the record
    seq = Sequence()
    bar_length = cast(float, config.bar_length)
    if bar_length != 0:
        if not Song.is_playing():
            seq.wait_for_event(SongStartedEvent)
        if not config.record_type.records_midi:
            # play well with the tail recording
            bar_length -= 0.6

        # this works because the method is called before the beginning of the bar
        seq.wait_bars(bar_length)
        seq.wait_for_event(BarChangedEvent)
    else:
        seq.wait_for_event(SongStoppedEvent)

    return seq.done()


class BaseRecorder(object):
    """Common recording operations"""

    def __init__(self, tracks: List[SimpleTrack], record_config: RecordConfig) -> None:
        self._tracks = tracks
        self.config = record_config

    def pre_record(self, clear_clips: bool) -> Sequence:
        seq = Sequence()
        if not Song.armed_tracks():
            seq.add(lambda: Song.selected_active_track().arm_state.arm_track())
        seq.add(partial(self._prepare_clip_slots_for_record, clear_clips=clear_clips))
        return seq.done()

    def _prepare_clip_slots_for_record(self, clear_clips: bool) -> Sequence:
        """isolating this, we need clip slots to be computed at runtime (if the track changes)"""
        seq = Sequence()
        seq.add(
            [
                partial(clip_slot.prepare_for_record, clear=clear_clips)
                for clip_slot in self.config.clip_slots
            ]
        )
        return seq.done()

    def cancel_record(self) -> None:
        for track in self._tracks:
            track._track.stop_all_clips(False)
