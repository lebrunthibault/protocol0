from protocol0.application.command.SerializableCommand import SerializableCommand


class SelectTrackByEnumCommand(SerializableCommand):
    def __init__(self, track_name: str) -> None:
        super(SelectTrackByEnumCommand, self).__init__()
        self.track_name = track_name
