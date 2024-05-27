import time
from dataclasses import dataclass, field
from typing import Optional, Callable, List

from _Framework.ButtonElement import ButtonElement
from _Framework.InputControlElement import MIDI_NOTE_TYPE, MIDI_CC_TYPE
from _Framework.SubjectSlot import subject_slot, SlotManager

from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils.error import log_exceptions
from protocol0.infra.midi.NoteSentEvent import NoteSentEvent
from protocol0.shared.AbstractEnum import AbstractEnum
from protocol0.shared.Song import find_track_or_none, find_track


class LEDColorVelocities(AbstractEnum):
    OFF = 12
    MUTED = 29
    ACTIVE = 62
    SOLO = 60


@dataclass(frozen=True)
class ControlledTrack:
    name: str
    solo_mute_note: int
    track_select_note: int
    volume_cc: int
    is_top_track: bool
    track_names: List[str] = field(default_factory=lambda: [])
    select_getter: Optional[Callable] = None

    @property
    def _main_track(self) -> SimpleTrack:
        return find_track(self.name, exact=False, is_top=self.is_top_track)

    @property
    def _tracks(self) -> List[SimpleTrack]:
        track_names = self.track_names or [self.name]
        return list(
            filter(
                None,
                [
                    find_track_or_none(name, exact=False, is_top=self.is_top_track)
                    for name in track_names
                ],
            )
        )

    @property
    def has_tracks(self) -> bool:
        return bool(self._tracks)

    @property
    def muted(self) -> bool:
        return any(t.muted for t in self._tracks)

    @property
    def soloed(self) -> bool:
        return any(t.solo for t in self._tracks)

    def toggle(self) -> None:
        for track in self._tracks:
            track.toggle()

    def solo_toggle(self) -> None:
        for track in self._tracks:
            track.solo_toggle()

    def select(self) -> None:
        if self.select_getter:
            self.select_getter().select()
        else:
            self._main_track.select()

    def set_volume(self, value: float) -> None:
        self._main_track.devices.mixer_device.volume.value = value


class TrackEncoder(SlotManager):
    LONG_PRESS_THRESHOLD = 0.25  # maximum time in seconds we consider a simple press

    def __init__(
        self,
        channel: int,
        controlled_track: ControlledTrack,
        component_guard: Callable,
    ) -> None:
        super(TrackEncoder, self).__init__()

        self.channel = channel - 1
        self._controlled_track = controlled_track

        with component_guard():
            self._solo_mute_listener.subject = ButtonElement(
                True, MIDI_NOTE_TYPE, self.channel, controlled_track.solo_mute_note
            )
            self._track_select_listener.subject = ButtonElement(
                True, MIDI_NOTE_TYPE, self.channel, controlled_track.track_select_note
            )
            self._volume_listener.subject = ButtonElement(
                True, MIDI_CC_TYPE, self.channel, controlled_track.volume_cc
            )

        self._pressed_at: Optional[float] = None

        Scheduler.defer(self.init_leds)

    def __repr__(self) -> str:
        return f"TrackEncoder('{self._controlled_track.name}')"

    @property
    def _is_long_pressed(self) -> bool:
        return bool(
            self._pressed_at and (time.time() - self._pressed_at) > self.LONG_PRESS_THRESHOLD
        )

    def _set_led(self, color: LEDColorVelocities, note: Optional[int] = None) -> None:
        note = note or self._controlled_track.solo_mute_note
        DomainEventBus.emit(NoteSentEvent(self.channel, note, color.value))

    def init_leds(self) -> None:
        if not self._controlled_track.has_tracks:
            self._set_led(LEDColorVelocities.OFF)
            self._set_led(LEDColorVelocities.OFF, self._controlled_track.track_select_note)
            return None

        self._set_led(LEDColorVelocities.MUTED, self._controlled_track.track_select_note)

        if self._controlled_track.muted:
            self._set_led(LEDColorVelocities.MUTED)
        else:
            self._set_led(LEDColorVelocities.ACTIVE)

    @subject_slot("value")
    @log_exceptions
    def _solo_mute_listener(self, value: int) -> None:
        if value:
            self._pressed_at = time.time()
            return None

        if not self._controlled_track.has_tracks:
            self._set_led(LEDColorVelocities.OFF)

        if self._is_long_pressed:
            self._controlled_track.solo_toggle()
        else:
            self._controlled_track.toggle()

        if self._controlled_track.soloed:
            self._set_led(LEDColorVelocities.SOLO)
        elif self._controlled_track.muted:
            self._set_led(LEDColorVelocities.MUTED)
        else:
            self._set_led(LEDColorVelocities.ACTIVE)

    @subject_slot("value")
    @log_exceptions
    def _track_select_listener(self, value: int) -> None:
        if not value:
            self._controlled_track.select()
            if self._controlled_track.has_tracks:
                self._set_led(LEDColorVelocities.MUTED, self._controlled_track.track_select_note)

    @subject_slot("value")
    @log_exceptions
    def _volume_listener(self, value: int) -> None:
        scaled_value = ((value / 127) * 0.6) + 0.35
        self._controlled_track.set_volume(scaled_value)
