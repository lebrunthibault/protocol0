import Live


class CurrentMonitoringStateUpdatedEvent(object):
    def __init__(self, track: Live.Track.Track):
        self.track = track
