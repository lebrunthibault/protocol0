from protocol0.application.command.ToggleReferenceTrackStereoModeCommand import (
    ToggleReferenceTrackStereoModeCommand,
)
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.set.MixingService import MixingService


class ToggleReferenceTrackStereoModeCommandHandler(CommandHandlerInterface):
    def handle(self, command: ToggleReferenceTrackStereoModeCommand) -> None:
        self._container.get(MixingService).toggle_adptr_stereo_mode(command.stereo_mode)
