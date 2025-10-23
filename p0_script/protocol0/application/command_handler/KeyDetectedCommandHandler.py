from protocol0.application.command.KeyDetectedCommand import (
    KeyDetectedCommand,
)
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.live_set.LiveSet import LiveSet


class KeyDetectedCommandHandler(CommandHandlerInterface):
    def handle(self, command: KeyDetectedCommand) -> None:
        self._container.get(LiveSet).on_key_detected(command.pitch)
