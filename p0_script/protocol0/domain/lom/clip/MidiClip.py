from __future__ import division

from functools import partial
from typing import List, Optional, Any

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

    def get_notes(self) -> List[Note]:
        if not self._clip:
            return []

        live_notes = self._clip.get_selected_notes_extended()

        if len(live_notes) == 0:
            live_notes = self._clip.get_notes_extended(0, 128, self.loop.start, self.length)

        clip_notes = list(map(Note, live_notes))

        # noinspection PyArgumentList,PyUnresolvedReferences
        # clip_notes.sort(key=lambda x: x.start)

        # return clip_notes
        return clip_notes

    def set_notes(self, notes: List[Note], replace: bool = False) -> Optional[Sequence]:
        if not self._clip:
            return None

        seq = Sequence()

        if replace:
            seq.add(partial(self._clip.remove_notes_extended, 0, 128, 0, self._clip.length))

        # seq.add(partial(self._clip.add_new_notes, [note.to_spec() for note in notes]))
        seq.add(partial(self._clip.apply_note_modifications, [note._live_note for note in notes]))

        seq.defer()
        return seq.done()

    def clear_notes(self) -> Optional[Sequence]:
        return self.set_notes([], replace=True)

    def clear_muted_notes(self) -> Optional[Sequence]:
        return self.set_notes([n for n in self.get_notes() if not n.muted], replace=True)

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
        notes = self.get_notes()
        if len(notes) == 0:
            return
        average_velo = sum([note.velocity for note in notes]) / len(notes)
        for note in notes:
            velocity_diff = note.velocity - average_velo
            if go_next:
                note.velocity += velocity_diff / (scaling_factor - 1)
            else:
                note.velocity -= velocity_diff / scaling_factor

            note.velocity = clamp(note.velocity, 1, 128)
        self.set_notes(notes)

    def crop(self) -> Optional[Sequence]:
        if self._clip:
            self._clip.crop()  # noqa

        return None
