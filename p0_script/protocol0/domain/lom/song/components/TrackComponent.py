import Live
from _Framework.SubjectSlot import subject_slot, SlotManager

from protocol0.domain.lom.track.SelectedTrackChangedEvent import SelectedTrackChangedEvent
from protocol0.domain.lom.track.abstract_track.AbstractTrackSelectedEvent import (
    AbstractTrackSelectedEvent,
)
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.shared.Song import Song


class TrackComponent(SlotManager):
    def __init__(self, song_view: Live.Song.Song.View) -> None:
        super(TrackComponent, self).__init__()
        self._song_view = song_view
        DomainEventBus.subscribe(AbstractTrackSelectedEvent, self._on_abstract_track_selected_event)
        self._selected_track_listener.subject = self._song_view  # Song is not hydrated

    @subject_slot("selected_track")
    def _selected_track_listener(self) -> None:
        DomainEventBus.emit(SelectedTrackChangedEvent())

    def un_solo_all_tracks(self) -> None:
        for track in Song.simple_tracks():
            track.solo = False

    def _on_abstract_track_selected_event(self, event: AbstractTrackSelectedEvent) -> None:
        track = Song.live_track_to_simple_track(event.live_track)
        if track.group_track:
            track.group_track.is_folded = False
        if Song.selected_track() != track.base_track:
            self._song_view.selected_track = track._track
