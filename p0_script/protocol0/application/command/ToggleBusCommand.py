from protocol0.application.command.SerializableCommand import SerializableCommand


class ToggleBusCommand(SerializableCommand):
    def __init__(self, bus_name: str):
        super(ToggleBusCommand, self).__init__()
        self.bus_name = bus_name
