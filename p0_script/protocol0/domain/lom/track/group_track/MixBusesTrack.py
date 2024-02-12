from typing import Optional

from protocol0.domain.lom.track.group_track.NormalGroupTrack import NormalGroupTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import route_track_to_bus
from protocol0.shared.Song import Song
from protocol0.shared.sequence.Sequence import Sequence


class MixBusesTrack(NormalGroupTrack):
    TRACK_NAME = "*"

    def on_added(self) -> Optional[Sequence]:
        super(MixBusesTrack, self).on_added()

        for track in Song.simple_tracks():
            if track != self and track not in self.sub_tracks:
                route_track_to_bus(track)

        return None
