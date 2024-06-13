import time
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Callable

from _Framework.ButtonElement import ButtonElement
from _Framework.InputControlElement import MIDI_NOTE_TYPE, MIDI_CC_TYPE
from _Framework.SubjectSlot import subject_slot, SlotManager

from protocol0.domain.lom.track.ControlledTracks import ControlledTracks
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils.error import log_exceptions
from protocol0.infra.midi.NoteSentEvent import NoteSentEvent


class LEDColorVelocities(Enum):
    OFF = 12
    MUTED = 29
    ACTIVE = 62
    SOLO = 60


@dataclass(frozen=True)
class MidiIdentifiers:
    solo_mute_note: int
    track_select_note: int
    volume_cc: int


class TrackEncoder(SlotManager):
    LONG_PRESS_THRESHOLD = 0.25  # maximum time in seconds we consider a simple press

    def __init__(
        self,
        channel: int,
        controlled_tracks: ControlledTracks,
        midi_identifiers: MidiIdentifiers,
        component_guard: Callable,
    ) -> None:
        super(TrackEncoder, self).__init__()

        self.channel = channel - 1
        self._controlled_tracks = controlled_tracks
        self._midi_identifiers = midi_identifiers

        with component_guard():
            self._solo_mute_listener.subject = ButtonElement(
                True, MIDI_NOTE_TYPE, self.channel, midi_identifiers.solo_mute_note
            )
            self._track_select_listener.subject = ButtonElement(
                True, MIDI_NOTE_TYPE, self.channel, midi_identifiers.track_select_note
            )
            self._volume_listener.subject = ButtonElement(
                True, MIDI_CC_TYPE, self.channel, midi_identifiers.volume_cc
            )

        self._pressed_at: Optional[float] = None

        Scheduler.defer(self.init_leds)

    def __repr__(self) -> str:
        return f"TrackEncoder('{self._controlled_tracks}')"

    @property
    def _is_long_pressed(self) -> bool:
        return bool(
            self._pressed_at and (time.time() - self._pressed_at) > self.LONG_PRESS_THRESHOLD
        )

    def _set_led(self, color: LEDColorVelocities, note: Optional[int] = None) -> None:
        note = note or self._midi_identifiers.solo_mute_note
        DomainEventBus.emit(NoteSentEvent(self.channel, note, color.value))

    def init_leds(self) -> None:
        if not self._controlled_tracks.has_tracks:
            self._set_led(LEDColorVelocities.OFF)
            self._set_led(LEDColorVelocities.OFF, self._midi_identifiers.track_select_note)
            return None

        self._set_led(LEDColorVelocities.MUTED, self._midi_identifiers.track_select_note)

        if self._controlled_tracks.muted:
            self._set_led(LEDColorVelocities.MUTED)
        else:
            self._set_led(LEDColorVelocities.ACTIVE)

    @subject_slot("value")
    @log_exceptions
    def _solo_mute_listener(self, value: int) -> None:
        if value:
            self._pressed_at = time.time()
            return None

        if not self._controlled_tracks.has_tracks:
            self._set_led(LEDColorVelocities.OFF)

        if self._is_long_pressed:
            self._controlled_tracks.solo_toggle()
        else:
            self._controlled_tracks.toggle()

        if self._controlled_tracks.soloed:
            self._set_led(LEDColorVelocities.SOLO)
        elif self._controlled_tracks.muted:
            self._set_led(LEDColorVelocities.MUTED)
        else:
            self._set_led(LEDColorVelocities.ACTIVE)

    @subject_slot("value")
    @log_exceptions
    def _track_select_listener(self, value: int) -> None:
        if not value:
            self._controlled_tracks.select()
            if self._controlled_tracks.has_tracks:
                self._set_led(LEDColorVelocities.MUTED, self._midi_identifiers.track_select_note)

    @subject_slot("value")
    @log_exceptions
    def _volume_listener(self, value: int) -> None:
        scaled_value = ((value / 127) * 0.6) + 0.35
        self._controlled_tracks.set_volume(scaled_value)
