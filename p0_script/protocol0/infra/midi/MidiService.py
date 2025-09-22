from typing import Optional, Tuple, Callable

from protocol0.application.CommandBus import CommandBus
from protocol0.application.command.SerializableCommand import SerializableCommand
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.infra.midi.MidiBytesReceivedEvent import MidiBytesReceivedEvent
from protocol0.infra.midi.MidiBytesSentEvent import MidiBytesSentEvent
from protocol0.infra.midi.NoteSentEvent import NoteSentEvent
from protocol0.shared.logging.Logger import Logger


class MidiService(object):
    _DEBUG = False
    _MIDI_STATUS_BYTES = {"note": 144, "cc": 176, "pc": 192}

    def __init__(self, send_midi: Callable) -> None:
        self._send_midi = send_midi

        DomainEventBus.subscribe(MidiBytesReceivedEvent, self._on_midi_bytes_received_event)
        DomainEventBus.subscribe(NoteSentEvent, self._on_note_sent_event)

    def _sysex_to_string(self, sysex: Tuple) -> str:
        return bytearray(sysex[1:-1]).decode()

    def _send_cc(self, value: int, channel: int = 0) -> None:
        self._send_formatted_midi_message("cc", channel, value, 1)

        def send_127() -> None:
            self._send_formatted_midi_message("cc", channel, value, 127)

        Scheduler.defer(send_127)

    def _send_formatted_midi_message(
        self, message_type: str, channel: int, value: int, value2: Optional[int] = None
    ) -> None:
        status = self._MIDI_STATUS_BYTES[message_type]
        status += channel
        msg = [status, value]
        if value2:
            msg.append(value2)
        Logger.info(f"MidiService sending : {message_type} {msg}")
        midi_message = tuple(msg)
        self._send_midi(midi_message)
        DomainEventBus.emit(MidiBytesSentEvent(midi_message))

    def _on_midi_bytes_received_event(self, event: MidiBytesReceivedEvent) -> None:
        # Check if this is an EC4 SysEx message
        if len(event.midi_bytes) > 4 and event.midi_bytes[:4] == (0xF0, 0x00, 0x00, 0x00):
            return

        # Try to parse as serialized command
        message = self._sysex_to_string(sysex=event.midi_bytes)
        if self._DEBUG:
            Logger.info("message: %s" % message)
        try:
            command = SerializableCommand.un_serialize(message)
            CommandBus.dispatch(command)
        except Exception as e:
            Logger.info(f"Midi bytes received error : {e}")
            Logger.info(event.midi_bytes)

    def send_ec4_select_group(self, group_number: int) -> None:
        """Send SysEx command to EC4 to select group (1-16)"""
        if not (1 <= group_number <= 16):
            raise ValueError("Group number must be between 1 and 16")

        # Convert to 0-based index for SysEx
        group_index = group_number - 1

        # EC4 select group SysEx
        sysex_message = (
            0xF0,
            0x00,
            0x00,
            0x00,
            0x4E,
            0x2C,
            0x1B,
            0x4E,
            0x24,
            0x10 | group_index,
            0xF7,
        )

        Logger.info(f"MidiService sending EC4 group select: group {group_number})")
        self._send_midi(sysex_message)
        DomainEventBus.emit(MidiBytesSentEvent(sysex_message))

    def _on_note_sent_event(self, event: NoteSentEvent) -> None:
        self._send_formatted_midi_message(
            "note", event.midi_channel, event.note_number, event.velocity
        )
