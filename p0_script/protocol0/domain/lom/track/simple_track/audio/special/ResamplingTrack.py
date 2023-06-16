from typing import Any

from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack


class ResamplingTrack(SimpleAudioTrack):
    TRACK_NAME = "Resampling"

    def stop(self, *a: Any, **k: Any) -> None:
        if any(clip.is_recording for clip in self.clips):
            return

        super(ResamplingTrack, self).stop(*a, **k)
