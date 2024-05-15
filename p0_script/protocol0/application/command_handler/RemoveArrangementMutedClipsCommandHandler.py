from protocol0.application.command.RemoveArrangementMutedClipsCommand import (
    RemoveArrangementMutedClipsCommand,
)
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.shared.Song import Song


class RemoveArrangementMutedClipsCommandHandler(CommandHandlerInterface):
    def handle(self, _: RemoveArrangementMutedClipsCommand) -> None:
        for track in Song.simple_tracks():
            track.remove_arrangement_muted_clips(Song.loop_start(), Song.loop_end())
