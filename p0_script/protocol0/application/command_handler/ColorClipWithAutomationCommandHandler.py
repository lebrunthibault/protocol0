from protocol0.application.command.ColorClipWithAutomationCommand import (
    ColorClipWithAutomationCommand,
)
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.track.TrackAutomationService import TrackAutomationService


class ColorClipWithAutomationCommandHandler(CommandHandlerInterface):
    def handle(self, command: ColorClipWithAutomationCommand) -> None:
        self._container.get(TrackAutomationService).color_clip_with_automation()
