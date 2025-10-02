from typing import Any

from _Framework.ControlSurface import ControlSurface

from protocol0.domain.lom.scene.SceneService import SceneService
from protocol0.application.Container import Container
from protocol0.application.ScriptDisconnectedEvent import ScriptDisconnectedEvent
from protocol0.application.ScriptResetActivatedEvent import ScriptResetActivatedEvent
from protocol0.domain.live_set.LiveSet import LiveSet
from protocol0.domain.lom.track.TrackMapperService import TrackMapperService
from protocol0.domain.shared.errors.ErrorRaisedEvent import ErrorRaisedEvent
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.infra.midi.MidiService import MidiService
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence


class Protocol0(ControlSurface):
    def __init__(self, c_instance: Any = None) -> None:
        super(Protocol0, self).__init__(c_instance=c_instance)

        self._initialize()

    def _initialize(self, reset: bool = False) -> None:
        if reset:
            self.disconnect(reset)

        # noinspection PyBroadException
        try:
            container = Container(self)
        except Exception as e:
            print(e)
            DomainEventBus.emit(ErrorRaisedEvent())
            return

        DomainEventBus.subscribe(ScriptResetActivatedEvent, lambda _: self._initialize(reset=True))
        container.get(TrackMapperService).tracks_listener()
        container.get(SceneService).scenes_listener()

        if Song.is_live_set():
            container._register(LiveSet(midi_service=container.get(MidiService)))

        Logger.info("P0 script loaded")

    def disconnect(self, reset: bool = False) -> None:
        if not reset:
            super(Protocol0, self).disconnect()

        DomainEventBus.emit(ScriptDisconnectedEvent())
        # without this, the events are going to be handled twice
        DomainEventBus.reset()
        Sequence.reset()

        for track in Song.all_simple_tracks():
            track.disconnect()
        for scene in Song.scenes():
            scene.disconnect()
