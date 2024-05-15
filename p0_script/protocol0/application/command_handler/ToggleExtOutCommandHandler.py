from protocol0.application.command.ToggleExtOutCommand import ToggleExtOutCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.shared.Song import Song


class ToggleExtOutCommandHandler(CommandHandlerInterface):
    def handle(self, _: ToggleExtOutCommand) -> None:
        Song.selected_track().toggle_ext_out_routing()
