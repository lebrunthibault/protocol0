from protocol0.application.command.ToggleMonoSwitchCommand import ToggleMonoSwitchCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger


class ToggleMonoSwitchCommandHandler(CommandHandlerInterface):
    def handle(self, _: ToggleMonoSwitchCommand) -> None:
        utility = Song.master_track().devices.get_one_from_enum(DeviceEnum.UTILITY)

        if utility:
            utility.toggle()
        else:
            Logger.error("Utility not found")
