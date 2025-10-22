import enum
from functools import partial
from typing import Optional, cast

from _Framework.SubjectSlot import subject_slot, SlotManager

import Live
from protocol0.domain.live_set.LiveSetNotes import (
    make_clip_monophonic,
    quantize_bar_notes,
    split_bar_notes,
)
from protocol0.domain.lom.clip.ClipCreatedOrDeletedEvent import ClipCreatedOrDeletedEvent
from protocol0.domain.lom.clip.ClipLoop import ClipLoop
from protocol0.domain.lom.clip.ClipRecordedEvent import ClipRecordedEvent
from protocol0.domain.lom.clip.MidiClip import MidiClip
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.song.SongStoppedEvent import SongStoppedEvent
from protocol0.domain.lom.track.simple_track.midi.SimpleMidiTrack import SimpleMidiTrack
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

        def unsubscribe_on_clip_captured() -> None:
            DomainEventBus.un_subscribe(ClipCreatedOrDeletedEvent, self._on_clip_captured)

        DomainEventBus.subscribe(SongStoppedEvent, unsubscribe_on_clip_captured)

        DomainEventBus.subscribe(ClipRecordedEvent, self._on_clip_recorded)

        self._bass_track_arm_listener.subject = self._bass_track._track

    @subject_slot("arm")
    def _bass_track_arm_listener(self) -> None:
        activate_pitch = self._bass_track.arm_state.is_armed

        if self._synth_track_pitch:
            Scheduler.defer(partial(setattr, self._synth_track_pitch, "is_enabled", activate_pitch))
        if self._piano_track_pitch:
            Scheduler.defer(partial(setattr, self._piano_track_pitch, "is_enabled", activate_pitch))

    @defer
    def _on_clip_captured(self, event: ClipCreatedOrDeletedEvent) -> None:
        clip = MidiClip(event.live_clip_slot.clip, 0)
        loop: ClipLoop = clip.loop

        if loop.total_bar_length >= 8:
            loop.bar_length = 8
        elif loop.total_bar_length >= 4:
            loop.bar_length = 4
        elif loop.total_bar_length >= 2:
            loop.bar_length = 2

        clip.quantize(0.5)

        # clip.stop(True)
        clip.fire()

        # Scheduler.defer(self._playback.stop_playing)

    @defer
    def _on_clip_recorded(self, event: ClipRecordedEvent) -> None:
        if event.clip in self._bass_track.clips:
            make_clip_monophonic(self._bass_track.clip_slots[event.clip.index])
        if event.clip in self._piano_track.clips:
            quantize_bar_notes(self._piano_track.clip_slots[event.clip.index])
        if event.clip in self._synth_track.clips:
            split_bar_notes(self._synth_track.clip_slots[event.clip.index])

    def capture_midi(self) -> None:
        seq = Sequence()
        if Song.tempo() < 120:
            seq.wait_for_event(Last16thPassedEvent)
        else:
            seq.wait_for_event(Last8thPassedEvent)
        seq.add(Song.capture_midi)
        seq.wait_for_event(ClipCreatedOrDeletedEvent)
        seq.defer()
        seq.add(
            partial(DomainEventBus.un_subscribe, ClipCreatedOrDeletedEvent, self._on_clip_captured)
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
