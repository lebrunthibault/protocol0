from protocol0.application.command.SerializableCommand import SerializableCommand


class ScrollSceneTracksCommand(SerializableCommand):
    def __init__(self, go_next: bool = False) -> None:
        super(ScrollSceneTracksCommand, self).__init__()
        self.go_next = go_next
