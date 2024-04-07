from protocol0.application.command.FireSelectedSceneCommand import FireSelectedSceneCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.scene.ScenePlaybackService import ScenePlaybackService
from protocol0.domain.shared.ApplicationView import ApplicationView
from protocol0.shared.Song import Song


class FireSelectedSceneCommandHandler(CommandHandlerInterface):
    def handle(self, _: FireSelectedSceneCommand) -> None:
        if ApplicationView.is_arrangement_visible():
            return None

        self._container.get(ScenePlaybackService).fire_scene(Song.selected_scene())
