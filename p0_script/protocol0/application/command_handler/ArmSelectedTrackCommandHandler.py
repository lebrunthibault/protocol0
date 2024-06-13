from typing import Optional

from protocol0.application.command.ArmSelectedTrackCommand import ArmSelectedTrackCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.shared.Song import Song
from protocol0.shared.sequence.Sequence import Sequence


class ArmSelectedTrackCommandHandler(CommandHandlerInterface):
    def handle(self, _: ArmSelectedTrackCommand) -> Optional[Sequence]:
        return Song.selected_track().arm_state.toggle()
