from protocol0.application.command.ToggleReferenceTrackFiltersCommand import (
    ToggleReferenceTrackFiltersCommand,
)
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.device_parameter.DeviceParamEnum import DeviceParamEnum
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger


class ToggleReferenceTrackFiltersCommandHandler(CommandHandlerInterface):
    def handle(self, _: ToggleReferenceTrackFiltersCommand) -> None:
        adptr = Song.master_track().devices.get_one_from_enum(
            DeviceEnum.ADPTR_METRIC_AB, all_devices=True
        )
        if adptr:
            adptr.get_parameter_by_name(DeviceParamEnum.FILTER_SWITCH).toggle()
            return None

        Logger.error("No reference plugin")
