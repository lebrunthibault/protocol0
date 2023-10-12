from protocol0.application.command.DuplicateSceneCommand import DuplicateSceneCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.song.components.SceneCrudComponent import SceneCrudComponent
from protocol0.shared.Song import Song


class DuplicateSceneCommandHandler(CommandHandlerInterface):
    def handle(self, _: DuplicateSceneCommand) -> None:
        self._container.get(SceneCrudComponent).duplicate_scene(
            Song.selected_scene(), play_scene=True
        )
