from typing import Any

import Live

from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.utils.utils import clamp


class Note(object):
    MIN_DURATION = 1 / 128

    def __init__(self, live_note: Live.Clip.MidiNote) -> None:
        super(Note, self).__init__()
        self._live_note = live_note

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, Note)
            and self.pitch == other.pitch
            and self._is_value_equal(self.start, other.start)
            and self._is_value_equal(self.duration, other.duration)
            and self.muted == other.muted
        )

    def __repr__(self, **k: Any) -> str:
        return "{start:%.2f, duration:%.2f, pitch:%s, vel:%s, muted: %s}" % (
            self.start,
            self.duration,
            self.pitch,
            self.velocity,
            self.muted,
        )

    def _is_value_equal(self, val1: float, val2: float, delta: float = 0.00001) -> bool:
        return abs(val1 - val2) < delta

    @property
    def pitch(self) -> int:
        return int(clamp(self._live_note.pitch, 0, 127))

    @pitch.setter
    def pitch(self, pitch: int) -> None:
        self._live_note.pitch = int(clamp(pitch, 0, 127))

    @property
    def start(self) -> float:
        return 0 if self._live_note.start_time < 0 else self._live_note.start_time

    @start.setter
    def start(self, start: float) -> None:
        self._live_note.start_time = max(float(0), start)

    @property
    def end(self) -> float:
        return self.start + self.duration

    @end.setter
    def end(self, end: float) -> None:
        self.duration = end - self.start

    @property
    def duration(self) -> float:
        if self._live_note.duration <= Note.MIN_DURATION:
            return Note.MIN_DURATION
        return self._live_note.duration

    @duration.setter
    def duration(self, duration: int) -> None:
        self._live_note.duration = max(0, duration)
        if self._live_note.duration == 0:
            raise Protocol0Error("A Note with a duration of 0 is not accepted")

    @property
    def velocity(self) -> float:
        # using float to make scaling precise
        if self._live_note.velocity < 0:
            return 0
        if self._live_note.velocity > 127:
            return 127
        return self._live_note.velocity

    @velocity.setter
    def velocity(self, velocity: float) -> None:
        self._live_note.velocity = clamp(velocity, 0, 127)

    @property
    def muted(self) -> bool:
        return self._live_note.mute

    @muted.setter
    def muted(self, muted: bool) -> None:
        self._live_note.mute = muted
