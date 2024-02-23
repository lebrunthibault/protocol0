from _Framework.SubjectSlot import subject_slot

from protocol0.domain.lom.song.components.TrackComponent import get_track_by_name
from protocol0.domain.lom.track.simple_track.midi.SimpleMidiTrack import (
    SimpleMidiTrack,
)
from protocol0.domain.shared.utils.timing import defer


class NerveTrack(SimpleMidiTrack):
    TRACK_NAME = "Nerve"

    @subject_slot("solo")
    @defer
    def _solo_listener(self) -> None:
        """Handle Cthulhu tracks"""
        if not self.solo:
            return

        drum_bus = get_track_by_name("DR Bus")
        if not drum_bus:
            return

        drum_bus.solo = True
