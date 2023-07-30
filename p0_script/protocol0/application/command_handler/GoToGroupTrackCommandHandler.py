from protocol0.application.command.GoToGroupTrackCommand import GoToGroupTrackCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.shared.ApplicationView import ApplicationView
from protocol0.shared.Song import Song


class GoToGroupTrackCommandHandler(CommandHandlerInterface):
    def handle(self, _: GoToGroupTrackCommand) -> None:
        if Song.selected_track().group_track is not None:
            Song.selected_track().group_track.select()
            ApplicationView.focus_session()
