from protocol0.application.command.ToggleReferenceTrackCommand import ToggleReferenceTrackCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.device_parameter.DeviceParamEnum import DeviceParamEnum
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger


class ToggleReferenceTrackCommandHandler(CommandHandlerInterface):
    def handle(self, _: ToggleReferenceTrackCommand) -> None:
        adptr = Song.master_track().devices.get_one_from_enum(DeviceEnum.ADPTR_METRIC_AB)
        if adptr:
            adptr.get_parameter_by_name(DeviceParamEnum.AB_SWITCH).toggle()
            return None

        reference = Song.master_track().devices.get_one_from_enum(DeviceEnum.REFERENCE)
        if reference:
            reference.get_parameter_by_name(DeviceParamEnum.ORIGINAL_REFERENCE).toggle()
            return None

        Logger.warning("No reference plugin")
