from protocol0.domain.lom.song.components.PlaybackComponent import PlaybackComponent
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.shared.sequence.Sequence import Sequence


class CountInInterface(object):
    def launch(
        self,
        playback_component: PlaybackComponent,
        track: SimpleTrack,
        solo_count_in: bool = True,
    ) -> Sequence:
        raise NotImplementedError
