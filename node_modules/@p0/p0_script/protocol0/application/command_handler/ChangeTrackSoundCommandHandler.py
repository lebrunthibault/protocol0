from protocol0.application.command.ChangeTrackSoundCommand import (
    ChangeTrackSoundCommand,
)
from protocol0.application.command_handler.CommandHandlerInterface import CommandHandlerInterface
from protocol0.domain.live_set.LiveSetSounds import change_track_sound


class ChangeTrackSoundCommandHandler(CommandHandlerInterface):
    def handle(self, command: ChangeTrackSoundCommand) -> None:
        change_track_sound(command.track_type, command.sound_index)
