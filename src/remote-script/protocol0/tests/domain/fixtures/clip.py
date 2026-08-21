from _Framework.SubjectSlot import Subject
from typing import List

from protocol0.tests.domain.fixtures.clip_view import AbletonClipView


class AbletonClip(Subject):
    __subject_events__ = (
        "playing_status",
        "loop_start",
        "loop_end",
        "looping",
        "start_marker",
        "end_marker",
        "name",
        "warping",
        "muted",
    )

    def __init__(self):
        self.name = "test"
        self.view = AbletonClipView()
        self.is_recording = False
        self.length = 4
        self.color_index = 0
        self.looping = True
        self.loop_start = 0
        self.loop_end = 4
        self.muted = False
        self.playing_position = 0
        self.start_marker = 0
        self.end_marker = 4
        self.is_audio_clip = False
        self.is_playing = False
        self.is_triggered = False
        # note specs: objects with pitch / start_time / duration / velocity / mute
        self._notes: List = []

    def fire(self):
        self.is_playing = True

    def stop(self):
        self.is_playing = False

    """ notes (windowed like the Live API: pitch range + time range) """

    def get_notes_extended(self, from_pitch, pitch_span, from_time, time_span):
        return [note for note in self._notes if self._in_window(note, from_pitch, pitch_span, from_time, time_span)]

    def add_new_notes(self, note_specs):
        self._notes.extend(note_specs)

    def remove_notes_extended(self, from_pitch, pitch_span, from_time, time_span):
        self._notes = [
            note
            for note in self._notes
            if not self._in_window(note, from_pitch, pitch_span, from_time, time_span)
        ]

    def apply_note_modifications(self, note_vector):
        pass  # the vector holds our note objects, already mutated in place

    @staticmethod
    def _in_window(note, from_pitch, pitch_span, from_time, time_span):
        return (
            from_pitch <= note.pitch < from_pitch + pitch_span
            and from_time <= note.start_time < from_time + time_span
        )

    # legacy selection-based API, kept as stubs
    # noinspection PyUnusedLocal
    def get_selected_notes_extended(self):
        return ()

    def select_all_notes(self):
        pass

    def replace_selected_notes(self, _):
        pass
