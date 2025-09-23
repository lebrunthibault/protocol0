from protocol0.application.command.ToggleCpuHeavyDevicesCommand import ToggleCpuHeavyDevicesCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.device.DeviceService import DeviceService


class ToggleCpuHeavyDevicesCommandHandler(CommandHandlerInterface):
    def handle(self, _: ToggleCpuHeavyDevicesCommand) -> None:
        self._container.get(DeviceService).toggle_cpu_heavy_devices()
