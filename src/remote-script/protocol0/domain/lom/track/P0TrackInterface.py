import Live
from typing import Protocol


class P0TrackInterface(Protocol):
    @property
    def _track(self) -> Live.Track.Track:
        raise NotImplementedError
