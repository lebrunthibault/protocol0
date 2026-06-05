from typing import Any

from _Framework.ControlSurface import ControlSurface

import protocol0.plugins as plugins_package
from protocol0.application.Container import Container
from protocol0.application.ScriptDisconnectedEvent import ScriptDisconnectedEvent
from protocol0.application.ScriptResetActivatedEvent import ScriptResetActivatedEvent
from protocol0.application.http import HttpServer
from protocol0.application.plugin.PluginLoader import PluginLoader
from protocol0.domain.lom.scene.SceneService import SceneService
from protocol0.domain.lom.track.TrackMapperService import TrackMapperService
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.backend.BackendClient import BackendClient
from protocol0.domain.shared.errors.ErrorRaisedEvent import ErrorRaisedEvent
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
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

        PluginLoader.load_and_start(plugins_package)

        if not Backend.client().ping():
            Logger.warning("Protocol0 backend is not running at %s" % BackendClient._BASE_URL)

        HttpServer.start(container)

        Logger.info("Protocol 0 script loaded")

    def disconnect(self, reset: bool = False) -> None:
        # Tear down our own resources FIRST, then let the base class release its
        # own (cf. Structure Void lifecycle guide: super().disconnect() last),
        # otherwise the framework dismantles its ButtonElements/listeners before
        # our teardown runs, leaving orphaned listeners on reload.
        HttpServer.stop()

        DomainEventBus.emit(ScriptDisconnectedEvent())
        # without this, the events are going to be handled twice
        DomainEventBus.reset()
        Sequence.reset()
        # stop the Live.Base.Timer; on reset a fresh Container starts a new one,
        # so the old timer must be killed here or it leaks (Container._disconnect
        # is never called -- teardown goes through ScriptDisconnectedEvent).
        Scheduler.reset()

        for track in Song.all_simple_tracks():
            track.disconnect()
        for scene in Song.scenes():
            scene.disconnect()

        # On reset we keep the ControlSurface object alive and rebuild the
        # Container, so we must NOT release the base class resources.
        if not reset:
            super(Protocol0, self).disconnect()
