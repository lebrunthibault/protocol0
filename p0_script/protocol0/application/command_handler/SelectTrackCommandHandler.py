from protocol0.application.command.SelectTrackCommand import SelectTrackCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.track.ControlledTracks import ControlledTracksRegistry
from protocol0.domain.lom.track.ControlledTracksEnum import ControlledTracksEnum
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.shared.Song import Song


class SelectTrackCommandHandler(CommandHandlerInterface):
    def handle(self, command: SelectTrackCommand) -> None:
        try:
            track_enum = ControlledTracksEnum[command.track_name]
        except KeyError:
            raise Protocol0Error(f"Unknown track enum '{command.track_name}'")

        if track_enum == ControlledTracksEnum.MASTER:
            Song.master_track().select()
        else:
            ControlledTracksRegistry[track_enum].select()
