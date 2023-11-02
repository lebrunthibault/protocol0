import re

from typing import List, Iterator, Optional

from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.lom.clip.ClipColorEnum import ClipColorEnum
from protocol0.domain.lom.clip_slot.ClipSlot import ClipSlot
from protocol0.domain.lom.track.group_track.MixBusTrack import MixBusTrack
from protocol0.domain.lom.track.group_track.ext_track.SimpleAudioExtTrack import SimpleAudioExtTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.lom.track.simple_track.audio.special.ResamplingTrack import ResamplingTrack
from protocol0.domain.shared.utils.timing import debounce
from protocol0.shared.Song import Song
from protocol0.shared.observer.Observable import Observable


class SceneClipSlot(object):
    def __init__(self, track: SimpleTrack, clip_slot: ClipSlot) -> None:
        self.track = track
        self.clip_slot = clip_slot
        self.is_main_clip = not isinstance(track, (SimpleAudioExtTrack, MixBusTrack))

    def __repr__(self) -> str:
        return "SceneClips(%s, %s)" % (self.track, self.clip)

    @property
    def clip(self) -> Optional[Clip]:
        if self.clip_slot.has_clip and not isinstance(self.track, ResamplingTrack):
            return self.clip_slot.clip
        else:
            return None


class SceneClips(Observable):
    def __init__(self, index: int) -> None:
        super(SceneClips, self).__init__()
        self.index = index
        self.clip_slot_tracks: List[SceneClipSlot] = []

        self.build()

    def __repr__(self) -> str:
        return "SceneClips(%s)" % self.index

    def __iter__(self) -> Iterator[Clip]:
        return iter(
            scene_cs.clip
            for scene_cs in self.clip_slot_tracks
            if scene_cs.clip is not None and scene_cs.is_main_clip
        )

    @property
    def all(self) -> List[Clip]:
        return [scene_cs.clip for scene_cs in self.clip_slot_tracks if scene_cs.clip is not None]

    @property
    def tracks(self) -> List[SimpleTrack]:
        return [scene_cs.track for scene_cs in self.clip_slot_tracks if scene_cs.clip is not None]

    @debounce(duration=50)
    def update(self, observable: Observable) -> None:
        if isinstance(observable, ClipSlot) or isinstance(observable, Clip):
            self.build()
            self.notify_observers()

    def build(self) -> None:
        self.clip_slot_tracks = []

        for track in Song.simple_tracks():
            # if self.index not in track.clip_slots:
            #     continue
            clip_slot = track.clip_slots[self.index]
            clip_slot.register_observer(self)
            self.clip_slot_tracks.append(SceneClipSlot(track, clip_slot))

        for clip in self:
            clip.register_observer(self)

    def on_added_scene(self) -> None:
        """Renames clips when doing consolidate time to new scene"""
        if any(clip for clip in self.all if self._clip_has_default_recording_name(clip)):
            for clip in self.all:
                if self._clip_has_default_recording_name(clip):
                    clip.appearance.color = ClipColorEnum.AUDIO_UN_QUANTIZED.value
                clip.clip_name.update("")

    def _clip_has_default_recording_name(self, clip: Clip) -> bool:
        return bool(re.match(".*\\[\\d{4}-\\d{2}-\\d{2} \\d+]$", clip.name))
