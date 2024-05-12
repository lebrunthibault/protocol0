from typing import Optional

from _Framework.SubjectSlot import subject_slot

from protocol0.domain.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.utils.timing import defer
from protocol0.shared.sequence.Sequence import Sequence


class NormalGroupTrack(AbstractGroupTrack):
    @classmethod
    def make(cls, base_group_track: SimpleTrack) -> "NormalGroupTrack":
        from protocol0.domain.lom.track.group_track.MixBusesTrack import MixBusesTrack

        if MixBusesTrack.TRACK_NAME == base_group_track.name.strip():
            return MixBusesTrack(base_group_track)
        else:
            return NormalGroupTrack(base_group_track)

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
