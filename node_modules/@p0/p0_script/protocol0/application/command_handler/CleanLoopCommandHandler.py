from protocol0.application.command.CleanLoopCommand import (
    CleanLoopCommand,
)
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger


class CleanLoopCommandHandler(CommandHandlerInterface):
    def handle(self, _: CleanLoopCommand) -> None:
        Logger.info(f"Removing clips from {Song.loop_start()} to {Song.loop_end()}")

        for track in Song.simple_tracks():
            track.remove_arrangement_muted_clips(Song.loop_start(), Song.loop_end())
