from typing import Any, Tuple

import Live

from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.utils.utils import clamp


class Note(object):
    MIN_DURATION = 1 / 128

    def __init__(
        self,
        pitch: int = 127,
        start: float = 0,
        duration: float = 1,
        velocity: int = 127,
        muted: bool = False,
    ) -> None:
        super(Note, self).__init__()
        self._pitch = int(pitch)
        self._start = start
        self._duration = duration
        self._velocity: float = int(velocity)
        self._muted = muted

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

    @classmethod
    def from_midi_note(cls, note: Live.Clip.MidiNote) -> "Note":
        return Note(
            pitch=note.pitch, start=note.start_time, duration=note.duration, velocity=note.velocity
        )

    def to_data(self) -> Tuple[int, float, float, int, bool]:
        return self.pitch, self.start, self.duration, int(self.velocity), self.muted

    def to_spec(self) -> Live.Clip.MidiNoteSpecification:
        # noinspection PyUnresolvedReferences
        from Live.Clip import MidiNoteSpecification as NoteSpec

        return NoteSpec(
            self.pitch, self.start, self.duration, velocity=self.velocity, mute=self.muted
        )

    def _is_value_equal(self, val1: float, val2: float, delta: float = 0.00001) -> bool:
        return abs(val1 - val2) < delta

    @property
    def pitch(self) -> int:
        return int(clamp(self._pitch, 0, 127))

    @pitch.setter
    def pitch(self, pitch: int) -> None:
        self._pitch = int(clamp(pitch, 0, 127))

    @property
    def start(self) -> float:
        return 0 if self._start < 0 else self._start

    @start.setter
    def start(self, start: float) -> None:
        self._start = max(float(0), start)

    @property
    def end(self) -> float:
        return self.start + self.duration

    @end.setter
    def end(self, end: float) -> None:
        self.duration = end - self.start

    @property
    def duration(self) -> float:
        if self._duration <= Note.MIN_DURATION:
            return Note.MIN_DURATION
        return self._duration

    @duration.setter
    def duration(self, duration: int) -> None:
        self._duration = max(0, duration)
        if self._duration == 0:
            raise Protocol0Error("A Note with a duration of 0 is not accepted")

    @property
    def velocity(self) -> float:
        # using float to make scaling precise
        if self._velocity < 0:
            return 0
        if self._velocity > 127:
            return 127
        return self._velocity

    @velocity.setter
    def velocity(self, velocity: float) -> None:
        self._velocity = clamp(velocity, 0, 127)

    @property
    def muted(self) -> bool:
        return self._muted

    @muted.setter
    def muted(self, muted: bool) -> None:
        self._muted = muted
