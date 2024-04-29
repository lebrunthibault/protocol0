from protocol0.application.command.SerializableCommand import SerializableCommand


class ToggleReferenceTrackStereoModeCommand(SerializableCommand):
    def __init__(self, stereo_mode: str):
        super(ToggleReferenceTrackStereoModeCommand, self).__init__()
        self.stereo_mode = stereo_mode
