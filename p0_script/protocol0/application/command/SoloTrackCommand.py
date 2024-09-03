from protocol0.application.command.SerializableCommand import SerializableCommand


class SoloTrackCommand(SerializableCommand):
    def __init__(self, track_name: str) -> None:
        super(SoloTrackCommand, self).__init__()
        self.track_name = track_name
