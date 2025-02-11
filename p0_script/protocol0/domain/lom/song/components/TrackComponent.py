import Live
from _Framework.SubjectSlot import SlotManager

from protocol0.domain.lom.track.simple_track.SimpleTrackSelectedEvent import (
    SimpleTrackSelectedEvent,
)
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.shared.Song import Song


class TrackComponent(SlotManager):
    def __init__(self, song_view: Live.Song.Song.View) -> None:
        super(TrackComponent, self).__init__()
        self._song_view = song_view
        DomainEventBus.subscribe(SimpleTrackSelectedEvent, self._on_simple_track_selected_event)

    def un_solo_all_tracks(self) -> None:
        for track in Song.simple_tracks():
            track.solo = False

    def _on_simple_track_selected_event(self, event: SimpleTrackSelectedEvent) -> None:
        track = Song.live_track_to_simple_track(event.live_track)
        if track.group_track:
            track.group_track.is_folded = False
