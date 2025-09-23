import Live


class TrackRoutingInterface(object):
    def __init__(self, live_track: Live.Track.Track) -> None:
        super(TrackRoutingInterface, self).__init__()
        self._live_track = live_track

    def __repr__(self) -> str:
        return self.__class__.__name__

    @property
    def live_track(self) -> Live.Track.Track:
        return self._live_track
