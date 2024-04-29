from protocol0.application.command.ToggleReferenceTrackCommand import ToggleReferenceTrackCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.device_parameter.DeviceParamEnum import DeviceParamEnum
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger


class ToggleReferenceTrackCommandHandler(CommandHandlerInterface):
    def handle(self, _: ToggleReferenceTrackCommand) -> None:
        adptr = Song.master_track().adptr

        if adptr:
            adptr.get_parameter_by_name(DeviceParamEnum.AB_SWITCH).toggle()
            return None

        Logger.error("No reference plugin")
