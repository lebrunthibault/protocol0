from protocol0.application.command.SerializableCommand import SerializableCommand


class ShowAutomationCommand(SerializableCommand):
    def __init__(self, go_next: bool = False) -> None:
        super(ShowAutomationCommand, self).__init__()
        self.go_next = go_next
