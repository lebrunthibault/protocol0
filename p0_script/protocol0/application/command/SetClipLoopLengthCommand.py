from protocol0.application.command.SerializableCommand import SerializableCommand


class SetClipLoopLengthCommand(SerializableCommand):
    def __init__(self, bar_length: int):
        super(SetClipLoopLengthCommand, self).__init__()
        self.bar_length = bar_length
