from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack


class SimpleTrackDisconnectedEvent(object):
    def __init__(self, track: "SimpleTrack") -> None:
        self.track = track
