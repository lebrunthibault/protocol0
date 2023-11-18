import Live
from typing import Optional

from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.observer.Observable import Observable
from protocol0.shared.sequence.Sequence import Sequence


class AbstractTrackArmState(Observable):
    def __init__(self, live_track: Live.Track.Track) -> None:
        super(AbstractTrackArmState, self).__init__()
        self._live_track = live_track

    @property
    def is_armed(self) -> bool:
        return False

    @is_armed.setter
    def is_armed(self, _: bool) -> None:
        pass

    def toggle(self) -> Optional[Sequence]:
        if not Song.selected_track().IS_ACTIVE:
            return None
        if self.is_armed:
            self.unarm()
            return None
        else:
            return self.arm()

    def arm(self) -> Optional[Sequence]:
        if self.is_armed:
            return None
        if self._live_track.is_foldable:
            # resetting this would select the track
            if self._live_track.fold_state:
                self._live_track.fold_state = False

        try:
            return self.arm_track()
        except RuntimeError:
            return None

    def arm_track(self) -> Optional[Sequence]:
        Logger.warning("Tried arming un-armable track")

        return None

    def unarm(self) -> None:
        self.is_armed = False
