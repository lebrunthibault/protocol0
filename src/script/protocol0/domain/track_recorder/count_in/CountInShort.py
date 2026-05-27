from protocol0.domain.lom.song.components.PlaybackComponent import PlaybackComponent
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.track_recorder.count_in.CountInInterface import CountInInterface
from protocol0.shared.sequence.Sequence import Sequence


class CountInShort(CountInInterface):
    def launch(
        self, playback_component: PlaybackComponent, _: SimpleTrack, __: bool = True
    ) -> Sequence:
        playback_component.stop_playing()
        seq = Sequence()
        seq.wait(40)  # mini count in
        return seq.done()
