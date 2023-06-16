import Live


class SimpleTrackArmedEvent(object):
    def __init__(self, live_track: Live.Track.Track) -> None:
        self.live_track = live_track
