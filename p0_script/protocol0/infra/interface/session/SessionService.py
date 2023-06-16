from _Framework.SessionComponent import SessionComponent
from typing import Optional, Callable

from protocol0.domain.lom.clip.ClipCreatedOrDeletedEvent import ClipCreatedOrDeletedEvent
from protocol0.domain.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from protocol0.domain.shared.SessionServiceInterface import SessionServiceInterface
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.infra.interface.session.SessionUpdatedEvent import SessionUpdatedEvent
from protocol0.shared.Song import Song


class SessionService(SessionServiceInterface):
    def __init__(self, component_guard: Callable, set_highlighting_session_component: Callable) -> None:
        super(SessionService, self).__init__()
        self._component_guard = component_guard
        self._set_highlighting_session_component = set_highlighting_session_component
        self._session: Optional[SessionComponent] = None
        DomainEventBus.subscribe(
            ClipCreatedOrDeletedEvent, lambda _: DomainEventBus.emit(SessionUpdatedEvent())
        )

    def toggle_session_ring(self) -> None:
        self._display_session_ring()
        self._hide_session_ring()

    def _display_session_ring(self) -> None:
        if self._session:
            self._hide_session_ring()

        try:
            if not Song.selected_track().IS_ACTIVE:
                return
        except IndexError:
            return

        total_tracks = []
        current_track = Song.current_track()
        if isinstance(current_track, AbstractGroupTrack):
            total_tracks = current_track.get_all_simple_sub_tracks()

        num_tracks = len([track for track in total_tracks if track.is_visible])
        track_offset = self._session_track_offset

        with self._component_guard():
            self._session = SessionComponent(num_tracks=num_tracks, num_scenes=8)
        self._session.set_offsets(
            track_offset=track_offset, scene_offset=Song.selected_scene().index
        )

    def _hide_session_ring(self) -> None:
        if self._session:
            self._session.set_show_highlight(False)
            self._session.disconnect()

    @property
    def _session_track_offset(self) -> int:
        return self._session.track_offset() if self._session else 0
