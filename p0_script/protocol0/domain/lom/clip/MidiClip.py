from __future__ import division

from functools import partial
from typing import List, Optional, Any, Iterable

import Live
from _Framework.SubjectSlot import subject_slot

from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.lom.note.Note import Note
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils.utils import clamp, track_base_name
from protocol0.shared.Config import Config
from protocol0.shared.Song import Song
from protocol0.shared.sequence.Sequence import Sequence


class MidiClip(Clip):
    def __init__(self, *a: Any, **k: Any) -> None:
        super(MidiClip, self).__init__(*a, **k)
        self._muted_listener.subject = self._clip

    def get_live_notes(self) -> Live.Clip.MidiNoteVector:
        if not self._clip:
            return []

        live_notes = self._clip.get_selected_notes_extended()

        if len(live_notes) == 0:
            live_notes = self._clip.get_notes_extended(0, 128, self.loop.start, self.length)

        return live_notes

    def get_notes(self) -> List[Note]:
        # return all notes not just the loop ones
        loop_start = self.loop.start
        self.loop.start = 0
        notes = list(map(Note.from_live_note, self.get_live_notes()))

        self.loop.start = loop_start
        return notes

    def get_looped_notes(self) -> List[Note]:
        """Return only loop section notes."""
        return list(map(Note.from_live_note, self.get_live_notes()))

    def replace_notes(self, notes: List[Note]) -> Optional[Sequence]:
        if not self._clip:
            return None

        seq = Sequence()

        seq.add(partial(self._clip.remove_notes_extended, 0, 128, 0, self.end_marker))
        seq.add(partial(self._clip.add_new_notes, [note.to_spec() for note in notes]))

        seq.defer()
        return seq.done()

    def clear_muted_notes(self) -> Optional[Sequence]:
        return self.replace_notes([n for n in self.get_notes() if not n.muted])

    @subject_slot("muted")
    def _muted_listener(self) -> None:
        if (
            not self.muted
            and track_base_name(Song.selected_track().name.lower()) in Config.FX_TRACK_NAMES
        ):

            def update_loop_length() -> None:
                length_diff = Song.selected_scene().length - self.length
                self.loop.start_marker -= length_diff
                self.loop.start -= length_diff

            if self.length < Song.selected_scene().length:
                Scheduler.defer(update_loop_length)

    def post_record(self, bar_length: int, quantize: bool) -> None:
        super(MidiClip, self).post_record(bar_length, quantize)

        if bar_length == 0:  # unlimited recording
            clip_end = int(self.loop.end) - (int(self.loop.end) % Song.signature_numerator())
            self.loop.end = clip_end

        if quantize:
            self._clip.view.grid_quantization = Live.Clip.GridQuantization.g_sixteenth
            self.scale_velocities(go_next=False, scaling_factor=2)
            self.quantize()

    def scale_velocities(self, go_next: bool, scaling_factor: int = 4) -> None:
        note_vector = self.get_live_notes()
        if len(list(note_vector)) == 0:
            return
        average_velo = sum([note.velocity for note in note_vector]) / len(note_vector)
        for note in note_vector:
            velocity_diff = note.velocity - average_velo
            if go_next:
                note.velocity += velocity_diff / (scaling_factor - 1)
            else:
                note.velocity -= velocity_diff / scaling_factor

            note.velocity = clamp(note.velocity, 1, 128)

        self.apply_note_modifications(note_vector)

    def apply_note_modifications(self, notes: Live.Clip.MidiNoteVector) -> None:
        self._clip.apply_note_modifications(notes)

    def crop(self) -> Optional[Sequence]:
        if self._clip:
            self._clip.crop()  # noqa

        return None
