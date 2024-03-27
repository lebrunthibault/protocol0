from protocol0.application.command.ToggleNotesCommand import ToggleNotesCommand
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.shared.Song import Song


class ToggleNotesCommandHandler(CommandHandlerInterface):
    def handle(self, _: ToggleNotesCommand) -> None:
        clip = Song.selected_clip(raise_if_none=False)

        if clip:
            clip.toggle_notes()
