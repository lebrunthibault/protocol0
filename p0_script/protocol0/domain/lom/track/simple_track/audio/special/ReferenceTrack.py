from protocol0.domain.lom.track.group_track.NormalGroupTrack import NormalGroupTrack
from protocol0.shared.Song import Song


class ReferenceTrack(NormalGroupTrack):
    TRACK_NAME = "Reference"

    def toggle(self) -> None:
        if self.muted:
            self.muted = False
            self.solo = True
            for device in Song.master_track().devices:
                device.is_enabled = False
        else:
            self.muted = True
            self.solo = False

            for device in Song.master_track().devices:
                device.is_enabled = True
