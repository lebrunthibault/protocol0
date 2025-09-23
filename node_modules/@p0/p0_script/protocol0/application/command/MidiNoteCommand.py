from protocol0.application.command.SerializableCommand import SerializableCommand


class MidiNoteCommand(SerializableCommand):
    def __init__(self, channel: int, note: int) -> None:
        super(MidiNoteCommand, self).__init__()
        self.channel = channel
        self.note = note
