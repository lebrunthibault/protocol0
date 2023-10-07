from types import MethodType

from _Framework.ControlSurface import ControlSurface, get_control_surfaces
from _Framework.Util import find_if
from protocol0.application.Protocol0 import Protocol0
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.infra.logging.LoggerService import LoggerService
from protocol0.infra.midi.MidiBytesReceivedEvent import MidiBytesReceivedEvent
from protocol0.infra.midi.MidiBytesSentEvent import MidiBytesSentEvent
from protocol0.shared.logging.LogLevelEnum import LogLevelEnum
from typing import Any, Tuple


class Protocol0Midi(ControlSurface):
    def __init__(self: Any, c_instance: bool = None) -> None:
        # hide initializing message
        log_message = self.log_message
        self.log_message = lambda a: True
        super(Protocol0Midi, self).__init__(c_instance=c_instance)
        self.log_message = log_message
        # stop log duplication
        self._c_instance.log_message = MethodType(lambda s, message: None, self._c_instance)  # noqa
        self.main_p0_script: Protocol0 = find_if(
            lambda s: type(s) == Protocol0, get_control_surfaces()
        )

        self._logger = LoggerService()

        if self.main_p0_script is None:
            self._logger.log("Error: couldn't find main Protocol0 script", level=LogLevelEnum.ERROR)
            return

        DomainEventBus.subscribe(MidiBytesSentEvent, self._on_midi_bytes_sent_event)

    def receive_midi(self, midi_bytes: Tuple) -> None:
        DomainEventBus.emit(MidiBytesReceivedEvent(midi_bytes))

    def _on_midi_bytes_sent_event(self, event: MidiBytesSentEvent) -> None:
        """Forward midi data to optional midi output ports (e.g. program change for Minitaur)"""
        self._send_midi(event.midi_bytes)
