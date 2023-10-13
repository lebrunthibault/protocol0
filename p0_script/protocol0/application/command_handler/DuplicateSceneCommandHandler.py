from protocol0.application.command.DuplicateSceneCommand import DuplicateSceneCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.scene.SceneService import SceneService


class DuplicateSceneCommandHandler(CommandHandlerInterface):
    def handle(self, _: DuplicateSceneCommand) -> None:
        self._container.get(SceneService).duplicate_scene()
