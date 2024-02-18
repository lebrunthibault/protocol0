from functools import partial
from typing import Optional

import Live
from _Framework.SubjectSlot import subject_slot

from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.track.simple_track.SimpleTrackService import rename_tracks
from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.lom.track.simple_track.midi.SimpleMidiTrack import (
    SimpleMidiTrack,
    toggle_note_track_routing,
)
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils.timing import defer
from protocol0.shared.Song import Song


class CthulhuTrack(SimpleMidiTrack):
    @classmethod
    def is_track_valid(cls, track: Live.Track.Track) -> bool:
        devices = list(track.devices)
        return len(devices) > 0 and any(d.name == DeviceEnum.CTHULHU.value for d in devices)

    @subject_slot("solo")
    @defer
    def _solo_listener(self) -> None:
        """Handle Cthulhu tracks"""
        if not self.solo:
            return

        synth_track: Optional[SimpleAudioTrack] = next(
            filter(lambda t: t.input_routing.track == self, Song.simple_tracks()), None  # type: ignore[arg-type]
        )
        if synth_track:
            synth_track.solo = True
        if Song.notes_track():
            Song.notes_track().solo = True

    def on_added(self) -> None:
        rename_tracks(list(Song.top_tracks()), self.name)
        assert Song.notes_track(), "No 'Notes' track"

        self.input_routing.track = Song.notes_track()  # type: ignore[assignment]
        self.select()

        if not self.synth_track:
            return

        rename_tracks(list(Song.top_tracks()), self.synth_track.name)

        self.synth_track.on_added()

        Scheduler.defer(partial(toggle_note_track_routing, self.synth_track))

    @property
    def synth_track(self) -> Optional[SimpleAudioTrack]:
        try:
            return list(Song.simple_tracks())[self.index + 1]
        except IndexError:
            return None
