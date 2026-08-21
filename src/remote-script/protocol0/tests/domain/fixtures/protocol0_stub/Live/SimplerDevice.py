from Live._meta import LomObject


class SimplerDevice(LomObject):
    class View(LomObject):
        pass


class PlaybackMode:
    classic = 0
    one_shot = 1
    slicing = 2
