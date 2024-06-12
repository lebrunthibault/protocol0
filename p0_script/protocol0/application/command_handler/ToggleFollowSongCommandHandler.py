from protocol0.application.command.ToggleFollowSongCommand import ToggleFollowSongCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.shared.Song import Song


class ToggleFollowSongCommandHandler(CommandHandlerInterface):
    def handle(self, _: ToggleFollowSongCommand) -> None:
        Song.view().follow_song = False
