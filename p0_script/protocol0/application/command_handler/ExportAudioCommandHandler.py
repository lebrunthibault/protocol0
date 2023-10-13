from protocol0.application.command.ExportAudioCommand import ExportAudioCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.set.AudioExportService import AudioExportService


class ExportAudioCommandHandler(CommandHandlerInterface):
    def handle(self, command: ExportAudioCommand) -> None:
        self._container.get(AudioExportService).export()
