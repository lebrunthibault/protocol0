from protocol0.application.command.ToggleLimiterCommand import ToggleLimiterCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger


class ToggleLimiterCommandHandler(CommandHandlerInterface):
    def handle(self, _: ToggleLimiterCommand) -> None:
        l2 = Song.master_track().devices.get_one_from_enum(DeviceEnum.L2_LIMITER)

        if l2:
            l2.is_enabled = not l2.is_enabled
        else:
            Logger.warning("L2 not found")
