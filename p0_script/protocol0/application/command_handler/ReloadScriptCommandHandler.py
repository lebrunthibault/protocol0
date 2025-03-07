from protocol0.application.command.ReloadScriptCommand import ReloadScriptCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.track.TrackMapperService import TrackMapperService
from protocol0.shared.logging.Logger import Logger


class ReloadScriptCommandHandler(CommandHandlerInterface):
    def handle(self, _: ReloadScriptCommand) -> None:
        Logger.clear()
        self._container.get(TrackMapperService).tracks_listener()
        # self._container.get(SceneService).scenes_listener()
