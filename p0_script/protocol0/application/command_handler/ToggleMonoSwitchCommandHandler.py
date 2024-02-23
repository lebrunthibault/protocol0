from protocol0.application.command.ToggleMonoSwitchCommand import ToggleMonoSwitchCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.song.components.TrackComponent import get_track_by_name
from protocol0.shared.logging.Logger import Logger


class ToggleMonoSwitchCommandHandler(CommandHandlerInterface):
    def handle(self, _: ToggleMonoSwitchCommand) -> None:
        pre_master = get_track_by_name("pre")
        assert pre_master, "No 'pre' track found"

        mono_switch = pre_master.devices.get_one_from_enum(DeviceEnum.MONO_SWITCH)

        if mono_switch:
            mono_switch.toggle()
        else:
            Logger.error("Mono switch not found")
