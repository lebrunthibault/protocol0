from protocol0.application.command.SerializableCommand import SerializableCommand


class KeyDetectedCommand(SerializableCommand):
    def __init__(self, pitch: int) -> None:
        super(KeyDetectedCommand, self).__init__()
        self.pitch = pitch
