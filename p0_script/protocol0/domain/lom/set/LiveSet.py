import enum
from functools import partial
from typing import Optional, cast

import Live
from _Framework.CompoundElement import subject_slot_group
from _Framework.SubjectSlot import SlotManager

from protocol0.domain.lom.clip.ClipCreatedOrDeletedEvent import ClipCreatedOrDeletedEvent
from protocol0.domain.lom.clip.ClipLoop import ClipLoop
from protocol0.domain.lom.clip.MidiClip import MidiClip
from protocol0.domain.lom.clip_slot.MidiClipSlot import MidiClipSlot
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.note.Note import Note
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.lom.track.simple_track.midi.SimpleMidiTrack import SimpleMidiTrack
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.BarChangedEvent import BarChangedEvent
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
    # VOCALS = "VOCALS"
    BASS = "BASS"
    SYNTH = "SYNTH"
    PIANO = "PIANO"

    def get(self) -> SimpleMidiTrack:
        return cast(SimpleMidiTrack, find_track(self.value.title(), exact=False))


class LiveSet(SlotManager):
    def __init__(self, midi_service: MidiService) -> None:
        super().__init__()
        self.midi_service = midi_service

        self._bass_track = LiveTrack.BASS.get()
        self._bass_track_pitch = self._bass_track.devices.get_one_from_enum(DeviceEnum.PITCH)
        self._synth_track = LiveTrack.SYNTH.get()
        self._synth_track_pitch = self._synth_track.devices.get_one_from_enum(DeviceEnum.PITCH)
        self._piano_track = LiveTrack.PIANO.get()

        self._bass_and_synth_tracks_arm_listener.replace_subjects(
            [self._bass_track._track, self._synth_track._track, self._piano_track._track]
        )

    @subject_slot_group("arm")
    def _bass_and_synth_tracks_arm_listener(self, _: Live.Track.Track) -> None:
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

    def capture_midi(self) -> None:
        DomainEventBus.subscribe(ClipCreatedOrDeletedEvent, self._on_clip_created)

        def fix_bass_clip() -> None:
            bass_track = LiveTrack.BASS.get()
            if bass_track.arm_state.is_armed:
                clip_slot = bass_track.clip_slots[Song.selected_scene().index]
                clip_slot.duplicate_clip_to(
                    bass_track.clip_slots[clip_slot.index - 1]
                )  # keep a copy
                self.make_bass_clip_monophonic(clip_slot)

        seq = Sequence()
        seq.add(Song.capture_midi)
        seq.wait_for_event(ClipCreatedOrDeletedEvent)
        seq.defer()
        seq.add(
            partial(DomainEventBus.un_subscribe, ClipCreatedOrDeletedEvent, self._on_clip_created)
        )
        seq.add(partial(self._container.get(MidiService).send_ec4_select_group, 9))
        seq.defer()
        seq.add(fix_bass_clip)
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
                seq.add(partial(self.make_bass_clip_monophonic, clip_slot))
                return seq.done()

        return None

    def make_bass_clip_monophonic(self, clip_slot: MidiClipSlot) -> None:
        clip_slot.clip.quantize()
        live_notes = clip_slot.clip.get_notes()
        if not live_notes:
            return

        notes = [Note(live_note) for live_note in live_notes]

        # Filter notes: keep only those with pitch <= C2 (MIDI note 36)
        bass_notes = [note for note in notes if note.pitch <= 48]

        if not bass_notes:
            return

        # Sort notes by start time for legato processing
        bass_notes.sort(key=lambda n: n.start)

        # # Make notes legato (connect them with no gaps) and clamp to C1-C2 range
        for i, note in enumerate(bass_notes):
            # Map pitch to C1-C2 range (36-48) preserving note name
            # Get note within octave (0-11), then map to C1-C2 range
            note_in_octave = note.pitch % 12
            note.pitch = 36 + note_in_octave  # C1 is 36, so add the note offset

            # Make legato: extend duration to next note's start time
            if i < len(bass_notes) - 1:
                next_note_start = bass_notes[i + 1].start
                if next_note_start > note.start:
                    note.duration = next_note_start - note.start
            else:
                # Last note: extend to end of clip
                note.end = clip_slot.clip.end_marker

        # Replace the notes in the clip
        clip_slot.clip.replace_notes(bass_notes)
