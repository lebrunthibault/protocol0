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
    solo_note: int
    mute_note: int
    volume_cc: int


class TrackEncoder(SlotManager):
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
            self._mute_listener.subject = ButtonElement(
                True, MIDI_NOTE_TYPE, self.channel, midi_identifiers.mute_note
            )
            self._solo_listener.subject = ButtonElement(
                True, MIDI_NOTE_TYPE, self.channel, midi_identifiers.solo_note
            )
            self._volume_listener.subject = ButtonElement(
                True, MIDI_CC_TYPE, self.channel, midi_identifiers.volume_cc
            )

        self._pressed_at: Optional[float] = None

        Scheduler.defer(self.init_leds)

    def __repr__(self) -> str:
        return f"TrackEncoder('{self._controlled_tracks}')"

    def _set_led(self, color: LEDColorVelocities, note: Optional[int]) -> None:
        note = note or self._midi_identifiers.solo_note
        DomainEventBus.emit(NoteSentEvent(self.channel, note, color.value))

    def init_leds(self) -> None:
        self._update_mute_led()
        self._update_solo_led()

    @subject_slot("value")
    @log_exceptions
    def _mute_listener(self, value: int) -> None:
        if value:
            return None

        if self._controlled_tracks.has_tracks:
            self._controlled_tracks.toggle()

        self._update_mute_led()

    def _update_mute_led(self) -> None:
        if not self._controlled_tracks.has_tracks:
            self._set_led(LEDColorVelocities.OFF, self._midi_identifiers.mute_note)
            return None

        if self._controlled_tracks.muted:
            self._set_led(LEDColorVelocities.MUTED, self._midi_identifiers.mute_note)
        else:
            self._set_led(LEDColorVelocities.ACTIVE, self._midi_identifiers.mute_note)

    @subject_slot("value")
    @log_exceptions
    def _solo_listener(self, value: int) -> None:
        if value:
            return None

        if self._controlled_tracks.has_tracks:
            self._controlled_tracks.solo_toggle()

        self._update_solo_led()

    def _update_solo_led(self) -> None:
        if not self._controlled_tracks.has_tracks:
            self._set_led(LEDColorVelocities.OFF, self._midi_identifiers.solo_note)
            return None

        if self._controlled_tracks.soloed:
            self._set_led(LEDColorVelocities.SOLO, self._midi_identifiers.solo_note)
        else:
            self._set_led(LEDColorVelocities.MUTED, self._midi_identifiers.solo_note)

    @subject_slot("value")
    @log_exceptions
    def _volume_listener(self, value: int) -> None:
        scaled_value = ((value / 127) * 0.6) + 0.35
        self._controlled_tracks.set_volume(scaled_value)
