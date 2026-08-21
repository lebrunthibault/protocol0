from dataclasses import dataclass
from typing import List

from protocol0.shared.Song import Song


@dataclass
class AbletonTrack:
    name: str
    color: int
    index: int
    live_id: int
    type: str
    muted: bool
    solo: bool
    armed: bool
    is_playing: bool
    devices: List[str]


@dataclass
class AbletonScene:
    index: int
    name: str


@dataclass
class AbletonSetCurrentState:
    selected_track: AbletonTrack
    tracks: List[AbletonTrack]
    scenes: List[AbletonScene]
    selected_scene_index: int
    tempo: float
    is_playing: bool


class AbletonSet(object):
    def __repr__(self) -> str:
        return "AbletonSet"

    def to_model(self, full: bool = True) -> AbletonSetCurrentState:
        tracks = []
        scenes = []
        if full:
            tracks = [AbletonTrack(**track.to_dict()) for track in Song.simple_tracks()]
            scenes = [AbletonScene(index=scene.index, name=scene.name) for scene in Song.scenes()]

        return AbletonSetCurrentState(
            selected_track=AbletonTrack(**Song.selected_track().to_dict()),
            tracks=tracks,
            scenes=scenes,
            selected_scene_index=Song.selected_scene().index,
            tempo=Song.tempo(),
            is_playing=Song.is_playing(),
        )
