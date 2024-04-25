from protocol0.application.command.ToggleReferenceTrackFiltersCommand import (
    ToggleReferenceTrackFiltersCommand,
)
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.device_parameter.DeviceParamEnum import DeviceParamEnum
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger


class ToggleReferenceTrackFiltersCommandHandler(CommandHandlerInterface):
    def handle(self, command: ToggleReferenceTrackFiltersCommand) -> None:
        adptr = Song.master_track().devices.get_one_from_enum(
            DeviceEnum.ADPTR_METRIC_AB, all_devices=True
        )
        if adptr:
            filter_switch = adptr.get_parameter_by_name(DeviceParamEnum.FILTER_SWITCH)

            if not filter_switch:
                Backend.client().show_warning("Filter Switch not enabled on ADPTR")
                return None

            if not command.filter_preset:
                filter_switch.toggle()
            else:
                filter_switch.value = filter_switch.max

                filter_preset = adptr.get_parameter_by_name(DeviceParamEnum.FILTER_PRESET)

                if not filter_preset:
                    Backend.client().show_warning("Filter Preset not enabled on ADPTR")

                filter_preset_to_value = {
                    "sub": 0.6,
                    "bass": 0.8,
                    "low_mid": 0,
                    "mid": 0.2,
                    "high": 0.4,
                }

                Logger.dev(filter_preset)
                Logger.dev(filter_preset_to_value[command.filter_preset.lower()])
                filter_preset.value = filter_preset_to_value[command.filter_preset.lower()]

            return None

        Logger.error("No reference plugin")
