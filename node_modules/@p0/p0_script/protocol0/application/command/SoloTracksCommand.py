from typing import Optional

from protocol0.application.command.SerializableCommand import SerializableCommand


class SoloTracksCommand(SerializableCommand):
    def __init__(self, solo_type: Optional[str] = None, bus_name: Optional[str] = None):
        super(SoloTracksCommand, self).__init__()
        self.solo_type = solo_type
        self.bus_name = bus_name
