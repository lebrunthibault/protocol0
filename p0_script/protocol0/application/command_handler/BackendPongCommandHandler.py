from protocol0.application.command.BackendPongCommand import (
    BackendPongCommand,
)
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface


class BackendPongCommandHandler(CommandHandlerInterface):
    def handle(self, command: BackendPongCommand) -> None:
        from protocol0.application.Protocol0 import Protocol0

        Protocol0._BACKEND_ALIVE = True
