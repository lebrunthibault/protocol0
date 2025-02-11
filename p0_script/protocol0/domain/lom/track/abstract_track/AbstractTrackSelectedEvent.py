import Live


class AbstractTrackSelectedEvent(object):
    """Used for searching and selecting tracks."""
    
    def __init__(self, live_track: Live.Track.Track) -> None:
        self.live_track = live_track
