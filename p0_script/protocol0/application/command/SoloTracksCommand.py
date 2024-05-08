from protocol0.application.command.SerializableCommand import SerializableCommand


class SoloTracksCommand(SerializableCommand):
    def __init__(self, solo_type: str):
        super(SoloTracksCommand, self).__init__()
        self.solo_type = solo_type
