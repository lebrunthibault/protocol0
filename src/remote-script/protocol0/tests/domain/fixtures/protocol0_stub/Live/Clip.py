from Live._meta import LomObject


class Clip(LomObject):
    class View(LomObject):
        pass


class WarpMode:
    beats = 0
    tones = 1
    texture = 2
    repitch = 3
    complex = 4
    rex = 5
    complex_pro = 6


class GridQuantization:
    no_grid = 0
    g_thirtysecond = 1
    g_sixteenth = 2
    g_eighth = 3
    g_quarter = 4
    g_half = 5
    g_bar = 6


class MidiNote(LomObject):
    pass


class MidiNoteVector(list):
    pass


class MidiNoteSpecification:
    def __init__(
        self,
        pitch=0,
        start_time=0.0,
        duration=0.0,
        velocity=100,
        mute=False,
        probability=1.0,
        velocity_deviation=0,
        release_velocity=64,
    ):
        self.pitch = pitch
        self.start_time = start_time
        self.duration = duration
        self.velocity = velocity
        self.mute = mute
        self.probability = probability
        self.velocity_deviation = velocity_deviation
        self.release_velocity = release_velocity
