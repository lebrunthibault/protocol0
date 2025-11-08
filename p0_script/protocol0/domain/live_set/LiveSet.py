import enum
from functools import partial
from typing import Optional, cast, List

from _Framework.SubjectSlot import subject_slot, SlotManager

import Live
from protocol0.domain.live_set.LiveSetNotes import (
    make_clip_monophonic,
    quantize_bar_notes,
    split_bar_notes,
    determine_captured_clip_bar_length,
)
from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.lom.clip.ClipCreatedEvent import ClipCreatedEvent
from protocol0.domain.lom.clip.ClipLoop import ClipLoop
from protocol0.domain.lom.clip.ClipRecordedEvent import ClipRecordedEvent
from protocol0.domain.lom.clip.MidiClip import MidiClip
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.device_parameter.DeviceParamEnum import DeviceParamEnum
from protocol0.domain.lom.note.Note import Note
from protocol0.domain.lom.song.SongStoppedEvent import SongStoppedEvent
from protocol0.domain.lom.track.simple_track.midi.SimpleMidiTrack import SimpleMidiTrack
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.BarChangedEvent import BarChangedEvent
from protocol0.domain.shared.scheduler.Last16thPassedEvent import Last16thPassedEvent
from protocol0.domain.shared.scheduler.Last8thPassedEvent import Last8thPassedEvent
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils.list import find_if
from protocol0.domain.shared.utils.timing import defer
from protocol0.infra.midi.MidiService import MidiService
from protocol0.shared.Song import Song, find_track
from protocol0.shared.logging.StatusBar import StatusBar
from protocol0.shared.sequence.Sequence import Sequence


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


class LiveSet(SlotManager):
    def __init__(self, midi_service: MidiService) -> None:
        super().__init__()
        self._midi_service = midi_service

        self._bass_track = LiveTrack.BASS.get()
        self._synth_track = LiveTrack.SYNTH.get()
        self._synth_track_pitch = self._synth_track.devices.get_one_from_enum(DeviceEnum.PITCH)
        self._piano_track = LiveTrack.PIANO.get()
        self._piano_track_pitch = self._piano_track.devices.get_one_from_enum(DeviceEnum.PITCH)
        self._vocal_track = LiveTrack.VOCALS.get()
        self._vocal_track_pitch = self._vocal_track.devices.get_one_from_enum(
            DeviceEnum.DRUM_RACK
        ).get_parameter_by_name(DeviceParamEnum.PITCH)

        def unsubscribe_on_clip_captured() -> None:
            DomainEventBus.un_subscribe(ClipCreatedEvent, self._on_clip_captured_event)

        DomainEventBus.subscribe(SongStoppedEvent, unsubscribe_on_clip_captured)

        DomainEventBus.subscribe(ClipRecordedEvent, self._on_clip_recorded_event)

        self._bass_track_arm_listener.subject = self._bass_track._track

    @property
    def instrument_tracks(self) -> List[SimpleMidiTrack]:
        return [
            self._bass_track,
            self._synth_track,
            self._piano_track,
        ]

    @subject_slot("arm")
    def _bass_track_arm_listener(self) -> None:
        activate_pitch = self._bass_track.arm_state.is_armed

        if self._synth_track_pitch:
            Scheduler.defer(partial(setattr, self._synth_track_pitch, "is_enabled", activate_pitch))
        if self._piano_track_pitch:
            Scheduler.defer(partial(setattr, self._piano_track_pitch, "is_enabled", activate_pitch))

    @defer
    def _on_clip_captured_event(self, event: ClipCreatedEvent) -> None:
        clip = event.clip_slot.clip

        if clip is None:
            raise Protocol0Warning("no clip on captured clip slot")

        loop: ClipLoop = clip.loop

        import logging

        logging.getLogger(__name__).info(f"clip captured: {clip}: {loop.total_bar_length}")

        loop.bar_length = determine_captured_clip_bar_length(clip)
        self._on_clip_recorded(clip)
        clip.quantize(0.5)

        # clip.stop(True)

        event.clip_slot.clip.fire()
        # event.clip_slot.fire(force_legato=True)

        # Scheduler.defer(self._playback.stop_playing)

    @defer
    def _on_clip_recorded_event(self, event: ClipRecordedEvent) -> None:
        self._on_clip_recorded(event.clip)

    def _on_clip_recorded(self, clip: Clip) -> None:
        if clip in self._bass_track.clips:
            make_clip_monophonic(self._bass_track.clip_slots[clip.index])
        if clip in self._piano_track.clips:
            quantize_bar_notes(self._piano_track.clip_slots[clip.index])
        if clip in self._synth_track.clips:
            split_bar_notes(self._synth_track.clip_slots[clip.index])

    def analyze_key(self) -> None:
        clip = (
            self._piano_track.playing_clip
            or self._synth_track.playing_clip
            or self._bass_track.playing_clip
        )

        def analyze_key_from_clip(midi_clip: MidiClip) -> None:
            notes_dict = [note.to_dict() for note in midi_clip.get_looped_notes()]
            Backend.client().post_analyze_key(notes_dict)

        if clip:
            analyze_key_from_clip(clip)
            return None

        # no playing clip we capture midi live
        if all(not track.arm_state.is_armed for track in self.instrument_tracks):
            raise Protocol0Warning("No playing clip and no instrument track armed")

        def clean_captured_clips() -> None:
            for track in self.instrument_tracks:
                if track.arm_state.is_armed:
                    track.playing_clip.delete()

        seq = Sequence()
        seq.add(self.capture_midi)
        seq.add(self.analyze_key)
        seq.add(clean_captured_clips)
        seq.done()

    def on_key_detected(self, pitch: int) -> None:
        keys = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]

        StatusBar.show_message(f"Detected major key: {keys[pitch]} -> pitch + {pitch * 127. / 12}")
        self._vocal_track_pitch.value = pitch * 127.0 / 11

    def capture_midi(self) -> None:
        DomainEventBus.subscribe(ClipCreatedEvent, self._on_clip_captured_event)

        seq = Sequence()
        if Song.tempo() < 120:
            seq.wait_for_event(Last16thPassedEvent)
        else:
            seq.wait_for_event(Last8thPassedEvent)
        seq.add(Song.capture_midi)
        seq.wait_for_event(ClipCreatedEvent)
        seq.defer()
        seq.add(
            partial(DomainEventBus.un_subscribe, ClipCreatedEvent, self._on_clip_captured_event)
        )
        seq.add(partial(self._midi_service.send_ec4_select_group, 9))
        seq.wait_for_event(BarChangedEvent)

        seq.done()

    def copy_piano_to_bass(self) -> Optional[Sequence]:
        piano_clip = self._piano_track.playing_clip

        if not piano_clip:
            raise Protocol0Warning("No piano playing clip")

        for clip_slot in self._bass_track.clip_slots:
            if clip_slot.index >= piano_clip.index:
                seq = Sequence()
                seq.add(
                    partial(
                        self._piano_track.clip_slots[piano_clip.index].duplicate_clip_to, clip_slot
                    )
                )
                seq.add(partial(make_clip_monophonic, clip_slot))
                return seq.done()

        return None
