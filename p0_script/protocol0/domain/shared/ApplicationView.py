from typing import Optional

import Live

from protocol0.domain.lom.song.components.RecordingComponent import RecordingComponent
from protocol0.domain.shared.SessionServiceInterface import SessionServiceInterface
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger


class ApplicationView(object):
    """Facade for accessing the application view"""

    _INSTANCE: Optional["ApplicationView"] = None

    def __init__(self, recording_component: RecordingComponent, application_view: Live.Application.Application.View, session_service: SessionServiceInterface) -> None:
        ApplicationView._INSTANCE = self
        self._recording_component = recording_component
        self._application_view = application_view
        self._session_service = session_service

    @classmethod
    def show_clip(cls) -> None:
        if not cls._INSTANCE._application_view.is_view_visible("Detail/Clip"):
            cls._INSTANCE._application_view.show_view("Detail")
            cls._INSTANCE._application_view.show_view("Detail/Clip")

    @classmethod
    def show_device(cls) -> None:
        """Shows track view."""
        cls._INSTANCE._application_view.show_view("Detail")
        cls._INSTANCE._application_view.show_view("Detail/DeviceChain")

    @classmethod
    def show_session(cls) -> None:
        cls._INSTANCE._application_view.show_view("Session")

    @classmethod
    def show_arrangement(cls) -> None:
        cls._INSTANCE._application_view.show_view("Arranger")
        cls._INSTANCE._recording_component.back_to_arranger = False

    @classmethod
    def show_browser(cls) -> None:
        cls._INSTANCE._application_view.show_view("Browser")

    @classmethod
    def focus_detail(cls) -> None:
        cls._focus_view("Detail")

    @classmethod
    def focus_session(cls) -> None:
        cls._focus_view("Session")

    @classmethod
    def focus_current_track(cls) -> None:
        """Moves the focus to the detail view."""
        try:
            selected_track = Song.selected_track()
        except Protocol0Error as e:
            Logger.error(str(e), show_notification=False)
            return

        is_visible = Song.selected_track().is_visible
        if Song.selected_track().group_track:
            Song.selected_track().group_track.is_folded = False
            # NB : unfolding parent classes will select them
            if Song.selected_track() != selected_track:
                selected_track.select()

            if not is_visible:
                # careful: this will impact the session display for long sets (scroll it up or down)
                cls._INSTANCE._session_service.toggle_session_ring()

    @classmethod
    def _focus_view(cls, view: str) -> None:
        """Moves the focus to the given view, showing it first if needed."""
        if not cls._INSTANCE._application_view.is_view_visible(view):
            cls._INSTANCE._application_view.show_view(view)
        cls._INSTANCE._application_view.focus_view(view)

    @classmethod
    def focus_device(cls) -> None:
        """Hack to bring device into view."""
        NAV_DIR = Live.Application.Application.View.NavDirection
        cls._INSTANCE._application_view.scroll_view(NAV_DIR.right, 'Detail/DeviceChain', False)
        cls._INSTANCE._application_view.scroll_view(NAV_DIR.left, 'Detail/DeviceChain', False)

    @classmethod
    def is_session_visible(cls) -> bool:
        return cls._INSTANCE._application_view.is_view_visible("Session")

    @classmethod
    def is_clip_view_visible(cls) -> bool:
        return cls._INSTANCE._application_view.is_view_visible("Detail/Clip")

    @classmethod
    def is_browser_visible(cls) -> bool:
        return cls._INSTANCE._application_view.is_view_visible("Browser")

    @classmethod
    def toggle_browse(cls) -> bool:
        return cls._INSTANCE._application_view.toggle_browse()
