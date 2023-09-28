from functools import partial

from protocol0.application.ScriptResetActivatedEvent import ScriptResetActivatedEvent
from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface
from protocol0.domain.lom.set.SessionToArrangementService import SessionToArrangementService
from protocol0.domain.lom.track.simple_track.SimpleTrackService import SimpleTrackService
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus


class ActionGroupSet(ActionGroupInterface):
    CHANNEL = 3

    def configure(self) -> None:
        # FREeZe tracks encoder
        self.add_encoder(
            identifier=3,
            name="select tracks to be frozen",
            on_press=self._container.get(SimpleTrackService).select_tracks_to_freeze,
        )
        # INIT song encoder
        self.add_encoder(
            identifier=4,
            name="(re) initialize the script",
            on_press=partial(DomainEventBus.emit, ScriptResetActivatedEvent()),
        )

        # Session2ARrangement encoder
        self.add_encoder(
            identifier=16,
            name="bounce session to arrangement",
            on_press=self._container.get(SessionToArrangementService).bounce_session_to_arrangement,
        )
