class AbstractTrackNameUpdatedEvent(object):
    def __init__(self, previous_name: str):
        self.previous_name = previous_name
