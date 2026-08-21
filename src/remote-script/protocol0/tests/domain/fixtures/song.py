from collections import namedtuple

from _Framework.SubjectSlot import Subject
from typing import List, Optional

from protocol0.tests.domain.fixtures.clip_slot import AbletonClipSlot
from protocol0.tests.domain.fixtures.scene import AbletonScene
from protocol0.tests.domain.fixtures.simple_track import AbletonTrack, TrackType
from protocol0.tests.domain.fixtures.song_view import AbletonSongView


class AbletonSong(Subject):
    __subject_events__ = (
        "is_playing",
        "record_mode",
        "tempo",
        "clip_trigger_quantization",
        "midi_recording_quantization",
        "re_enable_automation_enabled",
        "tracks",
        "scenes",
        "current_song_time",
    )

    def __init__(self) -> None:
        self.view = AbletonSongView()
        self.tempo = 120
        self.signature_numerator = 4

        first_track = AbletonTrack()
        first_track.name = "First"
        self.tracks = [first_track]
        self.return_tracks: List[AbletonTrack] = []
        self.master_track = AbletonTrack(track_type=TrackType.AUDIO)
        self.master_track.name = "Master"
        self.scenes = [AbletonScene()]
        self.clip_trigger_quantization = 0

        self.view.selected_track = self.tracks[0]
        self.view.selected_scene = self.scenes[0]
        self.is_playing = False

        self._sync_clip_slot_matrix()

    def __repr__(self) -> str:
        return "AbletonSong"

    """ transport """

    def start_playing(self) -> None:
        self.is_playing = True

    def stop_playing(self) -> None:
        self.is_playing = False

    def stop_all_clips(self, _: bool = True) -> None:
        pass

    def get_current_beats_song_time(self) -> namedtuple:
        beats_song_time = namedtuple("beats_song_time", ["bars", "beats", "sub_division", "ticks"])
        return beats_song_time(1, 1, 1, 1)

    def begin_undo_step(self) -> None:
        pass

    def end_undo_step(self) -> None:
        pass

    """ track crud (mutates the fake set, firing the tracks listeners) """

    def create_midi_track(self, Index: Optional[int] = None) -> None:  # noqa: N803 (Live API)
        self._insert_track(AbletonTrack(track_type=TrackType.MIDI), Index)

    def create_audio_track(self, Index: Optional[int] = None) -> None:  # noqa: N803 (Live API)
        self._insert_track(AbletonTrack(track_type=TrackType.AUDIO), Index)

    def duplicate_track(self, index: int) -> None:
        source = self.tracks[index]
        duplicate = AbletonTrack(track_type=source.track_type)
        duplicate.name = source.name
        self._insert_track(duplicate, index + 1)

    def delete_track(self, index: int) -> None:
        track = self.tracks[index]
        tracks = list(self.tracks)
        tracks.pop(index)
        if self.view.selected_track is track and tracks:
            self.view.selected_track = tracks[min(index, len(tracks) - 1)]
        self.tracks = tracks  # reassignment fires the "tracks" listeners
        self._sync_clip_slot_matrix()

    def _insert_track(self, track: AbletonTrack, index: Optional[int]) -> None:
        tracks = list(self.tracks)
        if index is None:
            index = len(tracks)
        tracks.insert(index, track)
        # give the new track its clip slot column before the listeners map it
        track.clip_slots = [AbletonClipSlot() for _ in self.scenes]
        self.tracks = tracks  # reassignment fires the "tracks" listeners
        self._sync_clip_slot_matrix()
        self.view.selected_track = track  # Live selects the created track

    """ scene crud (mutates the fake set, firing the scenes listeners) """

    def create_scene(self, index: int = -1) -> None:
        scenes = list(self.scenes)
        if index in (-1, len(scenes)) or index is None:
            index = len(scenes)
        scenes.insert(index, AbletonScene())
        self.scenes = scenes  # reassignment fires the "scenes" listeners
        self._sync_clip_slot_matrix()
        self.view.selected_scene = scenes[index]

    def duplicate_scene(self, index: int) -> None:
        scenes = list(self.scenes)
        duplicate = AbletonScene()
        duplicate.name = scenes[index].name
        scenes.insert(index + 1, duplicate)
        self.scenes = scenes
        self._sync_clip_slot_matrix()
        self.view.selected_scene = duplicate

    def delete_scene(self, index: int) -> None:
        scenes = list(self.scenes)
        scene = scenes.pop(index)
        if self.view.selected_scene is scene and scenes:
            self.view.selected_scene = scenes[min(index, len(scenes) - 1)]
        self.scenes = scenes
        self._sync_clip_slot_matrix()

    def _sync_clip_slot_matrix(self) -> None:
        """Invariant of the track x scene grid: every track has one clip slot per
        scene, and a scene's clip_slots is its cross-track row."""
        for track in self.tracks:
            if len(track.clip_slots) < len(self.scenes):
                track.clip_slots = track.clip_slots + [
                    AbletonClipSlot() for _ in range(len(self.scenes) - len(track.clip_slots))
                ]
            elif len(track.clip_slots) > len(self.scenes):
                track.clip_slots = track.clip_slots[: len(self.scenes)]

        for scene_index, scene in enumerate(self.scenes):
            scene.clip_slots = [track.clip_slots[scene_index] for track in self.tracks]
