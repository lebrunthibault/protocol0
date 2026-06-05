import Live


class SimpleTrackArmState(object):
    def __init__(self, live_track: Live.Track.Track) -> None:
        self._live_track = live_track

    @property
    def is_armed(self) -> bool:
        return self._live_track and self._live_track.can_be_armed and self._live_track.arm

    @is_armed.setter
    def is_armed(self, is_armed: bool) -> None:
        if self._live_track.can_be_armed:
            self._live_track.arm = is_armed

    def arm_track(self) -> None:
        if self.is_armed:
            return None
        if self._live_track.is_foldable:
            self._live_track.fold_state = not self._live_track.fold_state
        else:
            self._live_track.mute = False
            self.is_armed = True
