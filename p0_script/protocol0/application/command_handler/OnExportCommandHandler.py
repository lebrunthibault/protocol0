from protocol0.application.command.OnExportCommand import OnExportCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.set.AudioExportService import AudioExportService


class OnExportCommandHandler(CommandHandlerInterface):
    def handle(self, command: OnExportCommand) -> None:
        self._container.get(AudioExportService).on_export()
