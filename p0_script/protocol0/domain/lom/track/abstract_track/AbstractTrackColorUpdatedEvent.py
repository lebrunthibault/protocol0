class AbstractTrackColorUpdatedEvent(object):
    def __init__(self, previous_color: int):
        self.previous_color = previous_color
