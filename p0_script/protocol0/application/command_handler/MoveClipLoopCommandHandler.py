from protocol0.application.command.MoveClipLoopCommand import MoveClipLoopCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.shared.Song import Song


class MoveClipLoopCommandHandler(CommandHandlerInterface):
    def handle(self, command: MoveClipLoopCommand) -> None:
        clip = Song.selected_clip()
        if not clip:
            return

        clip.loop.move(forward=command.forward, bar=command.bar)
