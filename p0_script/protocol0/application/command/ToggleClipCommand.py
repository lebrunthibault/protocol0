from protocol0.application.command.SerializableCommand import SerializableCommand


class ToggleClipCommand(SerializableCommand):
    def __init__(self, track_name: str):
        super(ToggleClipCommand, self).__init__()
        self.track_name = track_name
