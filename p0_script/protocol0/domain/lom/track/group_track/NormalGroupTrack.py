from typing import Optional

from _Framework.SubjectSlot import subject_slot

from protocol0.domain.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from protocol0.domain.shared.utils.timing import defer
from protocol0.shared.Undo import Undo
from protocol0.shared.sequence.Sequence import Sequence


class NormalGroupTrack(AbstractGroupTrack):
    def on_added(self) -> Optional[Sequence]:
        super(NormalGroupTrack, self).on_added()

        audio_tracks = [t for t in self.sub_tracks if t.has_audio_output]
        sub_tracks_routing = set([t.output_routing.track for t in audio_tracks])

        if len(sub_tracks_routing) == 1:
            for sub_track in audio_tracks:
                sub_track.output_routing.track = self

            self.output_routing.track = list(sub_tracks_routing)[0]  # type: ignore[assignment]

        return None

    @subject_slot("solo")
    @defer
    def _solo_listener(self) -> None:
        if self.solo:
            for sub_track in self.sub_tracks:
                sub_track.solo = True

    def balance_levels_to_zero(self) -> None:
        bus_volume = self.base_track.volume
        Undo.begin_undo_step()

        self.base_track.volume = 0
        for sub_track in self.base_track.sub_tracks:
            sub_track.volume += bus_volume

        Undo.end_undo_step()
