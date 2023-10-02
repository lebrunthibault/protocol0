from protocol0.application.command.LogSelectedCommand import LogSelectedCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.audit.LogService import LogService


class LogSelectedCommandHandler(CommandHandlerInterface):
    def handle(self, command: LogSelectedCommand) -> None:
        self._container.get(LogService).log_current()
