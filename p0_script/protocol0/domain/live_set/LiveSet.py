import enum
from functools import partial
from typing import Optional, cast

from _Framework.CompoundElement import subject_slot_group
from _Framework.SubjectSlot import SlotManager

import Live
from protocol0.domain.live_set.LiveSetNotes import make_clip_monophonic
from protocol0.domain.lom.clip.ClipCreatedOrDeletedEvent import ClipCreatedOrDeletedEvent
from protocol0.domain.lom.clip.ClipLoop import ClipLoop
from protocol0.domain.lom.clip.MidiClip import MidiClip
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.song.components.PlaybackComponent import PlaybackComponent
from protocol0.domain.lom.song.components.RecordingComponent import RecordingComponent
from protocol0.domain.lom.track.simple_track.midi.SimpleMidiTrack import SimpleMidiTrack
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.BarChangedEvent import BarChangedEvent
from protocol0.domain.shared.scheduler.Last16thPassedEvent import Last16thPassedEvent
from protocol0.domain.shared.scheduler.Last8thPassedEvent import Last8thPassedEvent
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils.timing import defer
from protocol0.infra.midi.MidiService import MidiService
from protocol0.shared.Song import Song, find_track
from protocol0.shared.sequence.Sequence import Sequence


class LiveTrack(enum.Enum):
    KICK = "KICK"
    # HATS = "HATS"
    # PERC = "PERC"
    FX = "FX"
    VOCALS = "VOCALS"
    BASS = "BASS"
    SYNTH = "SYNTH"
    PIANO = "PIANO"

    def get(self) -> SimpleMidiTrack:
        return cast(SimpleMidiTrack, find_track(self.value.title(), exact=False))


class LiveSet(SlotManager):
    def __init__(self, midi_service: MidiService) -> None:
        super().__init__()
        self._midi_service = midi_service

        self._bass_track = LiveTrack.BASS.get()
        self._bass_track_pitch = self._bass_track.devices.get_one_from_enum(DeviceEnum.PITCH)
        self._synth_track = LiveTrack.SYNTH.get()
        self._synth_track_pitch = self._synth_track.devices.get_one_from_enum(DeviceEnum.PITCH)
        self._piano_track = LiveTrack.PIANO.get()

        # self._bass_and_synth_tracks_arm_listener.replace_subjects(
        #     [self._bass_track._track, self._synth_track._track, self._piano_track._track]
        # )

    @subject_slot_group("arm")
    def _bass_and_synth_tracks_arm_listener(self, _: Live.Track.Track) -> None:
        """Useful only if I want to play high bass notes when solo arming bass."""
        activate_bass_pitch = False
        activate_synth_pitch = False

        if self._bass_track.arm_state.is_armed:
            if self._synth_track.arm_state.is_armed:
                activate_bass_pitch = True
                activate_synth_pitch = True
            elif self._piano_track.arm_state.is_armed:
                activate_bass_pitch = True

        Scheduler.defer(partial(setattr, self._bass_track_pitch, "is_enabled", activate_bass_pitch))
        Scheduler.defer(
            partial(setattr, self._synth_track_pitch, "is_enabled", activate_synth_pitch)
        )

    @defer
    def _on_clip_created(self, event: ClipCreatedOrDeletedEvent) -> None:
        clip = MidiClip(event.live_clip_slot.clip, 0)
        loop: ClipLoop = clip.loop
        if loop.total_bar_length >= 4:
            loop.bar_length = 4
        elif loop.total_bar_length >= 2:
            loop.bar_length = 2

        # clip.stop(True)
        clip.fire()

        # Scheduler.defer(self._playback.stop_playing)

    def capture_midi(self) -> None:
        DomainEventBus.subscribe(ClipCreatedOrDeletedEvent, self._on_clip_created)

        def fix_bass_clip() -> None:
            bass_track = LiveTrack.BASS.get()
            if bass_track.arm_state.is_armed:
                clip_slot = bass_track.clip_slots[Song.selected_scene().index]
                make_clip_monophonic(clip_slot)

        seq = Sequence()
        if Song.tempo() < 120:
            seq.wait_for_event(Last16thPassedEvent)
        else:
            seq.wait_for_event(Last8thPassedEvent)
        seq.add(Song.capture_midi)
        seq.wait_for_event(ClipCreatedOrDeletedEvent)
        seq.defer()
        seq.add(fix_bass_clip)
        seq.add(
            partial(DomainEventBus.un_subscribe, ClipCreatedOrDeletedEvent, self._on_clip_created)
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
