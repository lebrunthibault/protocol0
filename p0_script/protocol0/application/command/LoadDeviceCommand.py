from protocol0.application.command.SerializableCommand import SerializableCommand


class LoadDeviceCommand(SerializableCommand):
    def __init__(self, enum_name: str, create_track: bool = False) -> None:
        super(LoadDeviceCommand, self).__init__()
        self.enum_name = enum_name
        self.create_track = create_track
