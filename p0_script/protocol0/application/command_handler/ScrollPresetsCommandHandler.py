from protocol0.application.command.ScrollPresetsCommand import ScrollPresetsCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.shared.Song import Song


class ScrollPresetsCommandHandler(CommandHandlerInterface):
    def handle(self, command: ScrollPresetsCommand) -> None:
        if Song.selected_track().instrument:
            Song.selected_track().instrument.preset_list.scroll(command.go_next)
