from protocol0.application.command.SoloSelectedTrackCommand import SoloSelectedTrackCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.shared.Song import Song


class SoloSelectedTrackCommandHandler(CommandHandlerInterface):
    def handle(self, _: SoloSelectedTrackCommand) -> None:
        Song.selected_track().solo_toggle()
