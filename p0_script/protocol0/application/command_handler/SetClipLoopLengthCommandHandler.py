from protocol0.application.command.SetClipLoopLengthCommand import SetClipLoopLengthCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.shared.Song import Song


class SetClipLoopLengthCommandHandler(CommandHandlerInterface):
    def handle(self, command: SetClipLoopLengthCommand) -> None:
        clip = Song.selected_clip()
        if not clip:
            return

        clip.loop.bar_length = command.bar_length
        clip.show_loop()