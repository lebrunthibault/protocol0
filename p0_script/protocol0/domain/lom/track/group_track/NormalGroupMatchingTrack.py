from functools import partial

from typing import Optional

from protocol0.domain.lom.track.group_track.matching_track.MatchingTrackClipColorManager import (
    MatchingTrackClipColorManager,
)
from protocol0.domain.lom.track.group_track.matching_track.MatchingTrackInterface import (
    MatchingTrackInterface,
)
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.shared.sequence.Sequence import Sequence


class NormalGroupMatchingTrack(MatchingTrackInterface):
    @property
    def clip_color_manager(self):
        # type: () -> Optional[MatchingTrackClipColorManager]
        return None

    def bounce(self):
        # type: () -> Sequence
        seq = Sequence()

        self._audio_track.input_routing.track = self._base_track
        self._audio_track.arm_state.arm()
        seq.add(self._base_track.save)
        seq.add(partial(Backend.client().show_success, "Please record clips"))

        return seq.done()
