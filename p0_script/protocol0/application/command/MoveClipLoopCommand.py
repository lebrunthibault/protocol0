from protocol0.application.command.SerializableCommand import SerializableCommand


class MoveClipLoopCommand(SerializableCommand):
    def __init__(self, forward: bool = True) -> None:
        super(MoveClipLoopCommand, self).__init__()
        self.forward = forward
