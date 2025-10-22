from protocol0.application.command.BackendPongCommand import (
    BackendPongCommand,
)
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface


class BackendPongCommandHandler(CommandHandlerInterface):
    def handle(self, command: BackendPongCommand) -> None:
        import logging

        logging.getLogger(__name__).info("ok")
        logging.getLogger(__name__).info("ok")
        logging.getLogger(__name__).info("ok")
        logging.getLogger(__name__).info("ok")
        logging.getLogger(__name__).info("ok")
        from protocol0.application.Protocol0 import Protocol0

        Protocol0._BACKEND_ALIVE = True
