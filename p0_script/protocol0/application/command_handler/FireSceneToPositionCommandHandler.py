from protocol0.application.CommandBus import CommandBus
from protocol0.application.command.FireSceneToPositionCommand import FireSceneToPositionCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.scene.ScenePlaybackService import ScenePlaybackService
from protocol0.domain.shared.ApplicationView import only_in_session_view
from protocol0.shared.Song import Song


class FireSceneToPositionCommandHandler(CommandHandlerInterface):
    @only_in_session_view
    def handle(self, command: FireSceneToPositionCommand) -> None:
        """
        command.bar_length :

        is None : we fire again the last scene
        == - 1 : we fire the last bar of the previous scene
        other number : we fire the selected scene at the selected bar position
        """

        fire_to_position = self._container.get(ScenePlaybackService).fire_scene_to_position
        selected_scene = Song.selected_scene()
        bar_length = command.bar_length

        if bar_length is None:
            fire_to_position(Song.last_manually_started_scene())
            return

        recent_command = CommandBus.get_recent_command(
            FireSceneToPositionCommand, 1, except_current=True
        )

        if recent_command and recent_command.bar_length is not None:
            bar_length += (recent_command.bar_length + 1) * 10

        fire_to_position(selected_scene, bar_length)
