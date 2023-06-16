from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack


class ExtArmedEvent(object):
    def __init__(self, track: SimpleAudioTrack, arm: bool = True) -> None:
        self.track = track
        self.arm = arm
