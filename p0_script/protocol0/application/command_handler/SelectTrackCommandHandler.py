from protocol0.application.command.SelectTrackCommand import SelectTrackCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.shared.Song import Song, find_track


class SelectTrackCommandHandler(CommandHandlerInterface):
    def handle(self, command: SelectTrackCommand) -> None:
        if command.track_name.lower() == "master":
            Song.master_track().select()
        else:
            find_track(command.track_name).select()
