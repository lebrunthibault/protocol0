from typing import List, Iterator, Optional

from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.lom.clip_slot.ClipSlot import ClipSlot
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.utils.timing import debounce
from protocol0.shared.Song import Song
from protocol0.shared.observer.Observable import Observable


class SceneClipSlot(object):
    def __init__(self, track: SimpleTrack, clip_slot: ClipSlot) -> None:
        self.track = track
        self.clip_slot = clip_slot

    def __repr__(self) -> str:
        return "SceneClips(%s, %s)" % (self.track, self.clip)

    @property
    def clip(self) -> Optional[Clip]:
        if self.clip_slot.has_clip:
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
            scene_cs.clip for scene_cs in self.clip_slot_tracks if scene_cs.clip is not None
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
