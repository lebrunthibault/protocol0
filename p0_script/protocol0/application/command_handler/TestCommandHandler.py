from protocol0.application.command.TestCommand import TestCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface


class TestCommandHandler(CommandHandlerInterface):
    def handle(self, _: TestCommand) -> None:
        pass
