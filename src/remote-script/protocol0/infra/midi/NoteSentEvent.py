class NoteSentEvent(object):
    def __init__(self, midi_channel: int, note_number: int, velocity: int):
        self.midi_channel = midi_channel
        self.note_number = note_number
        self.velocity = velocity
