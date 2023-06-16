from protocol0.domain.lom.track.group_track.ext_track.ExternalSynthTrack import (
    ExternalSynthTrack,
)


class ExtAudioRecordingEndedEvent(object):
    def __init__(self, track: ExternalSynthTrack) -> None:
        self.track = track
