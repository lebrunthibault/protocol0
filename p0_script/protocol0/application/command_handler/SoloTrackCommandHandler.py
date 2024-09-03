from protocol0.application.command.SoloTrackCommand import SoloTrackCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.track.ControlledTracks import ControlledTracksRegistry
from protocol0.domain.lom.track.ControlledTracksEnum import ControlledTracksEnum


class SoloTrackCommandHandler(CommandHandlerInterface):
    def handle(self, command: SoloTrackCommand) -> None:
        controlled_track = ControlledTracksRegistry[
            ControlledTracksEnum[command.track_name.upper()]
        ]
        if controlled_track.has_tracks:
            controlled_track.solo_toggle()
