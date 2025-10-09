from protocol0.application.command.SerializableCommand import SerializableCommand


class ChangeTrackSoundCommand(SerializableCommand):
    def __init__(self, track_type: str, sound_index: int):
        super().__init__()

        self.track_type = track_type
        self.sound_index = sound_index
