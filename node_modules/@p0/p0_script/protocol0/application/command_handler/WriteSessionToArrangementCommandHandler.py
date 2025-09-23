from protocol0.application.command.WriteSessionToArrangementCommand import (
    WriteSessionToArrangementCommand,
)
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.set.AudioExportService import AudioExportService
from protocol0.domain.shared.ApplicationView import only_in_session_view


class WriteSessionToArrangementCommandHandler(CommandHandlerInterface):
    @only_in_session_view
    def handle(self, command: WriteSessionToArrangementCommand) -> None:
        self._container.get(AudioExportService).write_session_to_arrangement()
