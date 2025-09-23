from protocol0.application.command.CollapseSelectedTrackCommand import CollapseSelectedTrackCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.shared.Song import Song


class CollapseSelectedTrackCommandHandler(CommandHandlerInterface):
    def handle(self, command: CollapseSelectedTrackCommand) -> None:
        Song.selected_track().is_collapsed = not Song.selected_track().is_collapsed
