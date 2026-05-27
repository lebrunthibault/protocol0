from dataclasses import dataclass
from typing import List

from protocol0.shared.Song import Song


@dataclass
class AbletonTrack:
    name: str
    color: int


@dataclass
class AbletonSetCurrentState:
    selected_track: AbletonTrack
    tracks: List[AbletonTrack]


class AbletonSet(object):
    def __repr__(self) -> str:
        return "AbletonSet"

    def to_model(self, full: bool = True) -> AbletonSetCurrentState:
        tracks = []
        if full:
            tracks = [AbletonTrack(**track.to_dict()) for track in Song.simple_tracks()]

        return AbletonSetCurrentState(
            selected_track=AbletonTrack(**Song.selected_track().to_dict()),
            tracks=tracks,
        )
