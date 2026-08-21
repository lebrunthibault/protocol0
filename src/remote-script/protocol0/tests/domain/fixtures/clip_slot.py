from _Framework.SubjectSlot import Subject

from protocol0.tests.domain.fixtures.clip import AbletonClip


class AbletonClipSlot(Subject):
    __subject_events__ = ("has_clip", "is_triggered")

    def __init__(self):
        self.clip = None
        self.has_clip = None
        self.has_stop_button = True
        self.playing_position = 0
        self.is_playing = False
        self.is_triggered = False

    def add_clip(self):
        self.clip = AbletonClip()
        self.has_clip = True

    def fire(self, force_legato=False):
        if self.clip is not None:
            self.clip.is_playing = True
            self.is_playing = True

    def stop(self):
        if self.clip is not None:
            self.clip.is_playing = False
        self.is_playing = False

    def create_clip(self, length):
        clip = AbletonClip()
        clip.length = length
        clip.loop_end = length
        clip.end_marker = length
        self.clip = clip  # set before has_clip: the listener maps self.clip
        self.has_clip = True

    def delete_clip(self):
        self.clip = None
        self.has_clip = False

    def duplicate_clip_to(self, other):
        duplicate = AbletonClip()
        duplicate.name = self.clip.name
        duplicate.length = self.clip.length
        duplicate._notes = list(self.clip._notes)
        other.clip = duplicate
        other.has_clip = True
