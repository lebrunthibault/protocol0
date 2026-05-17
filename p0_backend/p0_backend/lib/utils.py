import mido

from protocol0.application.command.SerializableCommand import SerializableCommand


def log_string(string) -> str:
    return str(string).replace("<", "\\<")


def make_sysex_message_from_command(command: SerializableCommand) -> mido.Message:
    assert isinstance(command, SerializableCommand), (
        "expected SerializableCommand, got %s" % command
    )
    message = command.serialize()
    b = bytearray(message.encode())
    b.insert(0, 0xF0)
    b.append(0xF7)
    return mido.Message.from_bytes(b)


def nop(*_, **__):
    pass


def nop_decorator(*_, **__):
    return nop
