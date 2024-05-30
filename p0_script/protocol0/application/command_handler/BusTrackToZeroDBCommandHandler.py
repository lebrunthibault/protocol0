from typing import cast

from protocol0.application.command.BusTrackToZeroDBCommand import BusTrackToZeroDBCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.track.group_track.NormalGroupTrack import NormalGroupTrack
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.shared.Song import Song


class BusTrackToZeroDBCommandHandler(CommandHandlerInterface):
    def handle(self, command: BusTrackToZeroDBCommand) -> None:
        if Song.selected_track() == Song.master_track():
            Song.master_track().balance_levels_to_zero()
        elif isinstance(Song.current_track(), NormalGroupTrack):
            cast(NormalGroupTrack, Song.current_track()).balance_levels_to_zero()
        else:
            raise Protocol0Error("Expected bus track or master")
