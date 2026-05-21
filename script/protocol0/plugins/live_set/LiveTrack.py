import enum
from typing import cast

from protocol0.domain.lom.track.simple_track.midi.SimpleMidiTrack import SimpleMidiTrack
from protocol0.shared.Song import find_track


class LiveTrack(enum.Enum):
    KICK = "KICK"
    HAT = "HAT"
    PERC = "PERC"
    FX = "FX"
    VOCALS = "VOCALS"
    BASS = "BASS"
    SYNTH = "SYNTH"
    PIANO = "PIANO"

    def get(self) -> SimpleMidiTrack:
        return cast(SimpleMidiTrack, find_track(self.value.title(), exact=False))

    def uses_simpler(self) -> bool:
        return self in (LiveTrack.HAT, LiveTrack.PERC, LiveTrack.VOCALS)
