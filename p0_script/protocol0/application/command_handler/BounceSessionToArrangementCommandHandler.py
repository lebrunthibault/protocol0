from protocol0.application.command.BounceSessionToArrangementCommand import BounceSessionToArrangementCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.set.SessionToArrangementService import SessionToArrangementService


class BounceSessionToArrangementCommandHandler(CommandHandlerInterface):
    def handle(self, command: BounceSessionToArrangementCommand) -> None:
        self._container.get(SessionToArrangementService).bounce_session_to_arrangement()
