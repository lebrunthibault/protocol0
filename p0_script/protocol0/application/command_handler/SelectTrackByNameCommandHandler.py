from protocol0.application.command.SelectTrackByNameCommand import SelectTrackByNameCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.shared.Song import Song, find_track


class SelectTrackByNameCommandHandler(CommandHandlerInterface):
    def handle(self, command: SelectTrackByNameCommand) -> None:
        from protocol0.shared.logging.Logger import Logger

        Logger.dev(command.track_name)
        if command.track_name.lower() == "master":
            Song.master_track().select()
        else:
            find_track(command.track_name).select()
