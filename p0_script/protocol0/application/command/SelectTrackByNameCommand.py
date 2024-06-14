from protocol0.application.command.SerializableCommand import SerializableCommand


class SelectTrackByNameCommand(SerializableCommand):
    def __init__(self, track_name: str) -> None:
        super(SelectTrackByNameCommand, self).__init__()
        self.track_name = track_name
