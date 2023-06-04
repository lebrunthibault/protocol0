import logging

from _Framework.ControlSurface import ControlSurface
from typing import Any

from protocol0.application.CommandBus import CommandBus
from protocol0.application.Container import Container
from protocol0.application.ScriptDisconnectedEvent import ScriptDisconnectedEvent
from protocol0.application.ScriptResetActivatedEvent import ScriptResetActivatedEvent
from protocol0.application.command.ReloadScriptCommand import ReloadScriptCommand
from protocol0.domain.shared.errors.ErrorRaisedEvent import ErrorRaisedEvent
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence


class Protocol0(ControlSurface):
    def __init__(self, c_instance=None):
        # type: (Any) -> None
        super(Protocol0, self).__init__(c_instance=c_instance)

        self._initialize()

    def _initialize(self, reset=False):
        # type: (bool) -> None
        if reset:
            self.disconnect(reset)

        # noinspection PyBroadException
        try:
            Container(self)
        except Exception as e:
            print(e)
            DomainEventBus.emit(ErrorRaisedEvent())
            return
        logging.info("container saved")

        DomainEventBus.subscribe(ScriptResetActivatedEvent, lambda _: self._initialize(reset=True))
        CommandBus.dispatch(ReloadScriptCommand())

        Logger.info("P0 script loaded")

    def disconnect(self, reset=False):
        # type: (bool) -> None
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
