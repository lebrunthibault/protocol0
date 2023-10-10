from protocol0.application.command.CaptureMidiCommand import CaptureMidiCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.track_recorder.RecordService import RecordService


class CaptureMidiCommandHandler(CommandHandlerInterface):
    def handle(self, command: CaptureMidiCommand) -> None:
        self._container.get(RecordService).capture_midi()
