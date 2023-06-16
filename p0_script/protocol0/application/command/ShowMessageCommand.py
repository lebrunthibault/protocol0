from protocol0.application.command.SerializableCommand import SerializableCommand


class ShowMessageCommand(SerializableCommand):
    def __init__(self, message: str) -> None:
        super(ShowMessageCommand, self).__init__()
        self.message = message
