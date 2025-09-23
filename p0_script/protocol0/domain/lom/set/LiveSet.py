import enum
from functools import partial
from typing import Optional

import Live
from _Framework.SubjectSlot import SlotManager
from _Framework.CompoundElement import subject_slot_group

from protocol0.domain.lom.clip_slot.MidiClipSlot import MidiClipSlot
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.shared.Song import find_track
from protocol0.shared.logging.StatusBar import StatusBar
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

    def get(self) -> SimpleTrack:
        return find_track(self.value.title(), exact=False)


class LiveSet(SlotManager):
    def __init__(self) -> None:
        super().__init__()
        from protocol0.shared.logging.Logger import Logger

        Logger.dev("activating Live set mode")
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

    def action_copy_piano_to_bass(self) -> Optional[Sequence]:
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
                seq.add(partial(self._make_bass_clip_monophonic, clip_slot))
                return seq.done()

        return None

    def _make_bass_clip_monophonic(self, clip_slot: MidiClipSlot) -> None:
        from protocol0.domain.lom.note.Note import Note

        live_notes = clip_slot.clip.get_notes()
        if not live_notes:
            return

        notes = [Note(live_note) for live_note in live_notes]
        import logging

        # logging.getLogger(__name__).info(notes)

        # Filter notes: keep only those with pitch <= C2 (MIDI note 36)
        bass_notes = [note for note in notes if note.pitch <= 48]
        logging.getLogger(__name__).info(bass_notes)

        if not bass_notes:
            return

        # Sort notes by start time for legato processing
        bass_notes.sort(key=lambda n: n.start)

        # Make notes legato (connect them with no gaps) and pitch down one octave
        for i, note in enumerate(bass_notes):
            # Pitch down one octave (subtract 12 semitones)
            # note.pitch = max(0, note.pitch - 12)

            # Make legato: extend duration to next note's start time
            if i < len(bass_notes) - 1:
                next_note_start = bass_notes[i + 1].start
                if next_note_start > note.start:
                    note.duration = next_note_start - note.start

        logging.getLogger(__name__).info(bass_notes)

        # Replace the notes in the clip
        clip_slot.clip.replace_notes(bass_notes)
