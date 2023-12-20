from protocol0.application.command.ToggleRackChainCommand import ToggleRackChainCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.device.DeviceService import DeviceService


class ToggleRackChainCommandHandler(CommandHandlerInterface):
    def handle(self, _: ToggleRackChainCommand) -> None:
        self._container.get(DeviceService).toggle_selected_rack_chain()
