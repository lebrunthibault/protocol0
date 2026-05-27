from functools import partial

from protocol0.domain.lom.song.components.PlaybackComponent import PlaybackComponent
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.scheduler.Last32thPassedEvent import Last32thPassedEvent
from protocol0.domain.track_recorder.count_in.CountInInterface import CountInInterface
from protocol0.shared.Song import Song
from protocol0.shared.sequence.Sequence import Sequence


class CountInOneBar(CountInInterface):
    def launch(
        self,
        playback_component: PlaybackComponent,
        track: SimpleTrack,
        solo_count_in: bool = True,
    ) -> Sequence:
        playback_component.stop()
        track_solo = track.solo

        if solo_count_in:
            track.solo = True

        playback_component.metronome = True
        playback_component.start_playing()

        seq = Sequence()
        seq.defer()
        seq.wait_for_event(Last32thPassedEvent, continue_on_song_stop=True)
        if solo_count_in:
            seq.add(partial(setattr, track, "solo", track_solo))
        seq.add(partial(self._stop_count_in, playback_component, track))
        seq.done()
        # we don't delay because we launch the scene at the same time
        # and launch the session record just after
        # this leaves 1 bar (because of quantization)
        return Sequence().defer().done()

    def _stop_count_in(self, playback_component: PlaybackComponent, track: SimpleTrack) -> None:
        if (
            len([clip for clip in Song.selected_scene().clips if not clip.muted]) >= 1
            and not track.solo
        ):
            playback_component.metronome = False
