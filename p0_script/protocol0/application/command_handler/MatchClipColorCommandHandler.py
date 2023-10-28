from protocol0.application.command.MatchClipColorCommand import MatchClipColorCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.track.group_track.matching_track.MatchingTrackService import (
    MatchingTrackService,
)


class MatchClipColorCommandHandler(CommandHandlerInterface):
    def handle(self, command: MatchClipColorCommand) -> None:
        self._container.get(MatchingTrackService).match_clip_colors()
