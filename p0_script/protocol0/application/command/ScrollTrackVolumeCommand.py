from protocol0.application.command.SerializableCommand import SerializableCommand


class ScrollTrackVolumeCommand(SerializableCommand):
    def __init__(self, go_next: bool = False) -> None:
        super(ScrollTrackVolumeCommand, self).__init__()
        self.go_next = go_next
