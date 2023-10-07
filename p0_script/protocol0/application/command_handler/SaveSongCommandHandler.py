from protocol0.application.command.SaveSongCommand import SaveSongCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.shared.Song import Song


class SaveSongCommandHandler(CommandHandlerInterface):
    def handle(self, _: SaveSongCommand) -> None:
        for track in Song.simple_tracks():
            track.on_set_save()
