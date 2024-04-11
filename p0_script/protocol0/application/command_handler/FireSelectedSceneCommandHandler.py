from protocol0.application.command.FireSelectedSceneCommand import FireSelectedSceneCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.scene.ScenePlaybackService import ScenePlaybackService
from protocol0.domain.shared.ApplicationView import only_in_session_view
from protocol0.shared.Song import Song


class FireSelectedSceneCommandHandler(CommandHandlerInterface):
    @only_in_session_view
    def handle(self, _: FireSelectedSceneCommand) -> None:
        self._container.get(ScenePlaybackService).fire_scene(Song.selected_scene())
