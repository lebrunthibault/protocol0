from Live._meta import LomObject


class Track(LomObject):
    class View(LomObject):
        pass


class RoutingTypeCategory:
    none = 0
    external = 1
    rewire = 2
    resampling = 3
    master = 4
    parent_group_track = 5
    audio_or_midi_in = 6
    invalid = 7


class DeviceInsertMode:
    default = 0
    selected_left = 1
    selected_right = 2
