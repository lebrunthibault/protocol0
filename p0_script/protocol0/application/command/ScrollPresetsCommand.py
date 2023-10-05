from protocol0.application.command.SerializableCommand import SerializableCommand


class ScrollPresetsCommand(SerializableCommand):
    def __init__(self, go_next: bool) -> None:
        super(ScrollPresetsCommand, self).__init__()
        self.go_next = go_next
