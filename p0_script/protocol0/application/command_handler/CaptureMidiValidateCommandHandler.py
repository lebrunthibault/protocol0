from protocol0.application.command.CaptureMidiValidateCommand import CaptureMidiValidateCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.track_recorder.RecordService import RecordService


class CaptureMidiValidateCommandHandler(CommandHandlerInterface):
    def handle(self, command: CaptureMidiValidateCommand) -> None:
        self._container.get(RecordService).capture_midi_validate()
