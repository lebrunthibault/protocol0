from protocol0.application.command.SelectClipCommand import SelectClipCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.track.ClipPlayerService import ClipPlayerService


class SelectClipCommandHandler(CommandHandlerInterface):
    def handle(self, command: SelectClipCommand) -> None:
        return self._container.get(ClipPlayerService).select_clip(command.track_name)
