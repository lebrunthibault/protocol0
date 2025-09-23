from protocol0.application.command.LoopSelectedClipCommand import LoopSelectedClipCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.shared.Song import Song


class LoopSelectedClipCommandHandler(CommandHandlerInterface):
    def handle(self, command: LoopSelectedClipCommand) -> None:
        Song.selected_clip().looping = True
