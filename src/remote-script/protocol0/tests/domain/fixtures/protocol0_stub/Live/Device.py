from Live._meta import LomObject


class Device(LomObject):
    class View(LomObject):
        pass


class DeviceType:
    undefined = 0
    instrument = 1
    audio_effect = 2
    midi_effect = 4
