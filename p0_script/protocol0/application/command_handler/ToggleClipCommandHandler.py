from protocol0.application.command.ToggleClipCommand import ToggleClipCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.track.ClipPlayerService import ClipPlayerService


class ToggleClipCommandHandler(CommandHandlerInterface):
    def handle(self, command: ToggleClipCommand) -> None:
        return self._container.get(ClipPlayerService).toggle_clip(command.track_name)
