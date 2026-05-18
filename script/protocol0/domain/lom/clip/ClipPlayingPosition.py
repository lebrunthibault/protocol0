import Live

from protocol0.domain.lom.clip.ClipLoop import ClipLoop
from protocol0.shared.Song import Song


class ClipPlayingPosition(object):
    def __init__(self, live_clip: Live.Clip.Clip, clip_loop: ClipLoop) -> None:
        self._live_clip = live_clip
        self._clip_loop = clip_loop

    def __repr__(self) -> str:
        return "position: %s / %s. beats left: %s" % (
            self.position,
            self._clip_loop.length,
            self.beats_left,
        )

    @property
    def position(self) -> float:
        return self._live_clip.playing_position - self._clip_loop.start_marker

    @property
    def beats_left(self) -> int:
        bar_offset = int(self._clip_loop.bar_offset) * Song.signature_numerator()

        return int(self._clip_loop.length - self.position + bar_offset)
