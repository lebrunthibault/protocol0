from typing import Optional, Callable

from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.infra.midi.MidiBytesSentEvent import MidiBytesSentEvent
from protocol0.infra.midi.NoteSentEvent import NoteSentEvent
from protocol0.infra.midi.SysexSentEvent import SysexSentEvent
from protocol0.shared.logging.Logger import Logger


class MidiService(object):
    _MIDI_STATUS_BYTES = {"note": 144, "cc": 176, "pc": 192}

    def __init__(self, send_midi: Callable) -> None:
        self._send_midi = send_midi

        DomainEventBus.subscribe(NoteSentEvent, self._on_note_sent_event)
        DomainEventBus.subscribe(SysexSentEvent, self._on_sysex_sent_event)

    def _send_cc(self, cc: int, channel: int = 0, value: int = 0) -> None:
        self._send_formatted_midi_message("cc", channel, cc, value)

    def _send_formatted_midi_message(
        self, message_type: str, channel: int, value: int, value2: Optional[int] = None
    ) -> None:
        status = self._MIDI_STATUS_BYTES[message_type]
        status += channel
        msg = [status, value]
        if value2:
            msg.append(value2)
        Logger.dev(f"MidiService sending : {message_type} {msg}")
        midi_message = tuple(msg)
        self._send_midi(midi_message)
        DomainEventBus.emit(MidiBytesSentEvent(midi_message))

    def _on_note_sent_event(self, event: NoteSentEvent) -> None:
        self._send_formatted_midi_message(
            "note", event.midi_channel, event.note_number, event.velocity
        )

    def _on_sysex_sent_event(self, event: SysexSentEvent) -> None:
        self._send_midi(event.message)
        DomainEventBus.emit(MidiBytesSentEvent(event.message))
