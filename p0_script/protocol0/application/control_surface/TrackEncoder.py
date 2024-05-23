import time
from typing import Optional, Callable

from _Framework.ButtonElement import ButtonElement
from _Framework.InputControlElement import MIDI_NOTE_TYPE, MIDI_CC_TYPE
from _Framework.SubjectSlot import subject_slot, SlotManager

from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils.error import log_exceptions
from protocol0.infra.midi.NoteSentEvent import NoteSentEvent
from protocol0.shared.AbstractEnum import AbstractEnum
from protocol0.shared.Song import find_track


class LEDColorVelocities(AbstractEnum):
    OFF = 12
    MUTED = 29
    ACTIVE = 62
    SOLO = 60


class TrackEncoder(SlotManager):
    LONG_PRESS_THRESHOLD = 0.25  # maximum time in seconds we consider a simple press

    def __init__(
        self,
        channel: int,
        track_select_note: int,
        solo_mute_note: int,
        volume_cc: int,
        track_name: str,
        is_top_track: bool,
        component_guard: Callable,
    ) -> None:
        super(TrackEncoder, self).__init__()

        self.channel = channel - 1
        self._track_name = track_name
        self._is_top_track = is_top_track
        self._track_select_note = track_select_note
        self._solo_mute_note = solo_mute_note

        with component_guard():
            self._track_select_listener.subject = ButtonElement(
                True, MIDI_NOTE_TYPE, self.channel, track_select_note
            )
            self._solo_mute_listener.subject = ButtonElement(
                True, MIDI_NOTE_TYPE, self.channel, solo_mute_note
            )
            self._volume_listener.subject = ButtonElement(
                True, MIDI_CC_TYPE, self.channel, volume_cc
            )

        self._pressed_at: Optional[float] = None

        Scheduler.defer(self.init_leds)

    def __repr__(self) -> str:
        return f"TrackEncoder('{self._track_name}')"

    @property
    def track(self) -> SimpleTrack:
        track = self._track_or_none
        assert track, f"Couldn't find track '{self._track_name}'"

        return track

    @property
    def _track_or_none(self) -> Optional[SimpleTrack]:
        return find_track(self._track_name, exact=False, is_top=self._is_top_track)

    @property
    def _is_long_pressed(self) -> bool:
        return bool(
            self._pressed_at and (time.time() - self._pressed_at) > self.LONG_PRESS_THRESHOLD
        )

    def _set_led(self, color: LEDColorVelocities, note: Optional[int] = None) -> None:
        note = note or self._solo_mute_note
        DomainEventBus.emit(NoteSentEvent(self.channel, note, color.value))

    def init_leds(self) -> None:
        track = self._track_or_none

        if not track:
            self._set_led(LEDColorVelocities.OFF)
            self._set_led(LEDColorVelocities.OFF, self._track_select_note)
            return None

        self._set_led(LEDColorVelocities.MUTED, self._track_select_note)

        if track.muted:
            self._set_led(LEDColorVelocities.MUTED)
        else:
            self._set_led(LEDColorVelocities.ACTIVE)

    @subject_slot("value")
    @log_exceptions
    def _solo_mute_listener(self, value: int) -> None:
        if value:
            self._pressed_at = time.time()
            return None

        if not self._track_or_none:
            self._set_led(LEDColorVelocities.OFF)

        if self._is_long_pressed:
            self.track.solo_toggle()
        else:
            self.track.toggle()

        if self.track.solo:
            self._set_led(LEDColorVelocities.SOLO)
        elif self.track.muted:
            self._set_led(LEDColorVelocities.MUTED)
        else:
            self._set_led(LEDColorVelocities.ACTIVE)

    @subject_slot("value")
    @log_exceptions
    def _track_select_listener(self, value: int) -> None:
        if not value:
            self.track.select()

    @subject_slot("value")
    @log_exceptions
    def _volume_listener(self, value: int) -> None:
        scaled_value = ((value / 127) * 0.6) + 0.35
        self.track.devices.mixer_device.volume.value = scaled_value
