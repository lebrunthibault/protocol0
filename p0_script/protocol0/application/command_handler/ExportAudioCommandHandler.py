from protocol0.application.command.ExportAudioCommand import ExportAudioCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.set.AudioExportService import AudioExportService
from protocol0.domain.shared.ApplicationView import only_in_session_view


class ExportAudioCommandHandler(CommandHandlerInterface):
    @only_in_session_view
    def handle(self, command: ExportAudioCommand) -> None:
        self._container.get(AudioExportService).export()
