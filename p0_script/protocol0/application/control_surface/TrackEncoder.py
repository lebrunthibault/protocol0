from enum import Enum
from typing import Optional, Callable
import enum
from dataclasses import field, dataclass
from typing import List, Dict

from _Framework.ButtonElement import ButtonElement
from _Framework.InputControlElement import MIDI_NOTE_TYPE, MIDI_CC_TYPE
from _Framework.SubjectSlot import subject_slot, SlotManager

from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.ValueScroller import ValueScroller
from protocol0.shared.Song import Song, find_track_or_none, find_track


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


class ControlledTrack(enum.Enum):
    pass
    # MASTER = "MASTER"
    #
    # DRUMS = "DRUMS"
    # KICK = "KICK"
    # HATS = "HATS"
    # PERC = "PERC"
    # FX = "FX"
    # VOCALS = "VOCALS"
    # HARMONY = "HARMONY"
    # MELODY = "MELODY"
    # BASS = "BASS"


@dataclass(frozen=True)
class ControlledTracks:
    enum: ControlledTrack
    is_top_track: bool = True
    track_names: List[str] = field(default_factory=lambda: [])
    skip_group_track: bool = False

    def __repr__(self) -> str:
        return self.enum.name

    @property
    def _bus_name(self) -> str:
        return self.enum.value.title()

    @property
    def _main_track(self) -> SimpleTrack:
        return find_track(self._bus_name, exact=False, is_top=self.is_top_track)

    @property
    def _tracks(self) -> List[SimpleTrack]:
        track_names = self.track_names or [self._bus_name]
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

    def get(self) -> SimpleTrack:
        return self._main_track

    def toggle(self) -> None:
        for track in self._tracks:
            track.toggle()

    def solo_toggle(self) -> None:
        for track in self._tracks:
            track.solo_toggle()

    def select(self) -> SimpleTrack:
        tracks = [] if self.skip_group_track else [self._main_track]
        tracks += self._main_track.sub_tracks

        track_to_select: SimpleTrack = ValueScroller.scroll_values(
            tracks, Song.selected_track(), True
        )
        track_to_select.select()

        return track_to_select

    def set_volume(self, value: float) -> None:
        self._main_track.devices.mixer_device.volume.value = value


# track layout for prod
# ProdTrackRegistry: Dict[ControlledTrack, ControlledTracks] = {
#     ControlledTrack.DRUMS: ControlledTracks(ControlledTrack.DRUMS),
#     ControlledTrack.KICK: ControlledTracks(
#         ControlledTrack.KICK, is_top_track=False, skip_group_track=True
#     ),
#     ControlledTrack.HATS: ControlledTracks(
#         ControlledTrack.HATS, is_top_track=False, skip_group_track=True
#     ),
#     ControlledTrack.PERC: ControlledTracks(
#         ControlledTrack.PERC,
#         is_top_track=False,
#         track_names=["Perc", "FX"],
#         skip_group_track=True,
#     ),
#     ControlledTrack.FX: ControlledTracks(
#         ControlledTrack.FX,
#         is_top_track=False,
#         skip_group_track=True,
#     ),
#     ControlledTrack.VOCALS: ControlledTracks(ControlledTrack.VOCALS),
#     ControlledTrack.HARMONY: ControlledTracks(ControlledTrack.HARMONY),
#     ControlledTrack.MELODY: ControlledTracks(ControlledTrack.MELODY),
#     ControlledTrack.BASS: ControlledTracks(ControlledTrack.BASS, skip_group_track=True),
# }


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
