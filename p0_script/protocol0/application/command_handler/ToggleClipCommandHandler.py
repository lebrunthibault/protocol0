from protocol0.application.command.ToggleClipCommand import ToggleClipCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.song.components.TrackComponent import get_track_by_name
from protocol0.domain.lom.track.ClipPlayerService import ClipPlayerService
from protocol0.domain.lom.track.group_track.TrackCategoryEnum import TrackCategoryEnum


class ToggleClipCommandHandler(CommandHandlerInterface):
    def handle(self, command: ToggleClipCommand) -> None:
        track = get_track_by_name(command.track_name)
        if track is None:
            return

        if track.has_category(TrackCategoryEnum.DRUMS):
            self._container.get(ClipPlayerService).select_clip(track)
        else:
            self._container.get(ClipPlayerService).toggle_clip(track)
