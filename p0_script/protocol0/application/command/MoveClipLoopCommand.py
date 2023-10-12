from protocol0.application.command.SerializableCommand import SerializableCommand


class MoveClipLoopCommand(SerializableCommand):
    def __init__(self, forward: bool, bar: bool) -> None:
        super(MoveClipLoopCommand, self).__init__()
        self.forward = forward
        self.bar = bar
