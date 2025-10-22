from typing import Any

from _Framework.ControlSurface import ControlSurface

from protocol0.application.Container import Container
from protocol0.application.ScriptDisconnectedEvent import ScriptDisconnectedEvent
from protocol0.application.ScriptResetActivatedEvent import ScriptResetActivatedEvent
from protocol0.domain.live_set.LiveSet import LiveSet
from protocol0.domain.lom.scene.SceneService import SceneService
from protocol0.domain.lom.track.TrackMapperService import TrackMapperService
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.errors.ErrorRaisedEvent import ErrorRaisedEvent
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.infra.midi.MidiService import MidiService
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.logging.StatusBar import StatusBar
from protocol0.shared.sequence.Sequence import Sequence


class Protocol0(ControlSurface):
    _BACKEND_ALIVE = False

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
            container._register(LiveSet(container.get(MidiService)))

        Backend.client().ping()
        seq = Sequence()
        seq.wait_ms(3000)
        seq.add(Backend.client().ping)
        seq.wait_ms(5000)
        seq.add(self._check_backend_is_alive)
        seq.done()

        Logger.info("P0 script loaded")

    def _check_backend_is_alive(self) -> None:
        if not Protocol0._BACKEND_ALIVE:
            StatusBar.show_message("Protocol0 backend is not running")
            Backend.client().ping()

        seq = Sequence()
        seq.wait_ms(5000)
        seq.add(self._check_backend_is_alive)
        seq.done()

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
