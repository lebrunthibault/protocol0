from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.infra.midi.SysexSentEvent import SysexSentEvent
from protocol0.shared.logging.Logger import Logger


def send_ec4_select_group(group_number: int) -> None:
    """Send SysEx command to EC4 to select group (1-16)"""
    if not (1 <= group_number <= 16):
        raise ValueError("Group number must be between 1 and 16")

    group_index = group_number - 1

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

    Logger.info(f"EC4 group select: group {group_number}")
    DomainEventBus.emit(SysexSentEvent(sysex_message))
