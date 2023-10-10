from protocol0.application.command.SerializableCommand import SerializableCommand


class SelectClipCommand(SerializableCommand):
    def __init__(self, track_name: str):
        super(SelectClipCommand, self).__init__()
        self.track_name = track_name
