from typing import List

import Live

from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.utils.utils import float_seq


class ClipAutomationEnvelope(object):
    _FOOTPRINT_MEASURES = 100

    def __init__(self, envelope: Live.Clip.AutomationEnvelope, length: float) -> None:
        self._envelope = envelope
        self._length = length

    def __repr__(self) -> str:
        return f"ClipAutomationEnvelope({self.hash})"

    @property
    def hash(self) -> float:
        return hash(tuple(self.get_values()))

    def get_values(self) -> List[float]:
        """pick up x values"""
        values = [
            round(self.value_at_time(i), 4)
            for i in float_seq(0, int(self._length), self._length / self._FOOTPRINT_MEASURES)
        ]
        values.append(self.value_at_time(self._length))

        return values

    @property
    def start(self) -> float:
        return self.value_at_time(0)

    @property
    def end(self) -> float:
        return self.value_at_time(self._length)

    @property
    def is_linear(self) -> bool:
        start = self.start
        end = self.end
        values = []
        for i in range(self._FOOTPRINT_MEASURES + 1):
            val = start + (i * (end - start) / self._FOOTPRINT_MEASURES)
            values.append(round(val, 4))

        return hash(tuple(values)) == self.hash

    def equals(self, value: float) -> bool:
        """Checks the automation equals a single value"""
        return (
            self.is_linear
            and self.value_at_time(0) == value
            and self.value_at_time(self._length) == value
        )

    def value_at_time(self, beat_length: float) -> float:
        return self._envelope.value_at_time(beat_length)

    def insert_step(self, start_beat: float, beat_length: float, value: float) -> None:
        self._envelope.insert_step(start_beat, beat_length, value)

    def create_start_and_end_points(self, value: float = None) -> None:
        """we need to emulate an automation value at the beginning and the end of the clip
        so that doing ctrl-a will select the automation on the whole clip duration
        """
        if value is not None:
            self.insert_step(0, self._length, value)
        else:
            self.insert_step(0, 0, self.start)
            self.insert_step(self._length, 0, 0)

    def copy(self) -> None:
        self.create_start_and_end_points()
        Backend.client().select_and_copy()

    def paste(self) -> None:
        self.create_start_and_end_points()
        Backend.client().select_and_paste()

    @classmethod
    def focus(cls) -> None:
        Backend.client().move_to(1225, 1013)
