from typing import Any

from protocol0.application.command.SerializableCommand import SerializableCommand


class EmitBackendEventCommand(SerializableCommand):
    def __init__(self, event: str, data: Any = None) -> None:
        super(EmitBackendEventCommand, self).__init__()
        self.event = event
        self.data = data
