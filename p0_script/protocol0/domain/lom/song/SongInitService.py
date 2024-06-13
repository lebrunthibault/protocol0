from protocol0.domain.lom.set.AbletonSet import AbletonSet
from protocol0.domain.lom.song.SongInitializedEvent import SongInitializedEvent
from protocol0.domain.lom.song.components.PlaybackComponent import PlaybackComponent
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.shared.Song import Song
from protocol0.shared.sequence.Sequence import Sequence


class SongInitService(object):
    def __init__(
        self,
        playback_component: PlaybackComponent,
        ableton_set: AbletonSet,
    ) -> None:
        self._playback_component = playback_component
        self._ableton_set = ableton_set

    def init_song(self) -> Sequence:
        DomainEventBus.emit(SongInitializedEvent())

        seq = Sequence()
        seq.wait(2)
        selected_track = Song.selected_track()
        seq.add(selected_track.select)
        seq.wait(8)

        return seq.done()
