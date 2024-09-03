from protocol0.application.command.SerializableCommand import SerializableCommand


class MuteTrackCommand(SerializableCommand):
    def __init__(self, track_name: str) -> None:
        super(MuteTrackCommand, self).__init__()
        self.track_name = track_name
