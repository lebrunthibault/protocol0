from protocol0.application.command.RemoveMutedNotesCommand import (
    RemoveMutedNotesCommand,
)
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.lom.clip.MidiClip import MidiClip
from protocol0.shared.Song import Song


class RemoveMutedNotesCommandHandler(CommandHandlerInterface):
    def handle(self, _: RemoveMutedNotesCommand) -> None:
        clip = Song.selected_clip()
        assert isinstance(clip, MidiClip)

        clip.clear_muted_notes()
