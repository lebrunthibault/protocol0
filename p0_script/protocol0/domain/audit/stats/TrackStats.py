import collections
from typing import Dict

from protocol0.shared.Song import Song


class TrackStats(object):
    def to_dict(self) -> Dict:
        output = collections.OrderedDict()

        muted_tracks = [
            track
            for track in Song.simple_tracks()
            if not track.is_foldable
            and (all(clip.muted for clip in track.clips) or track.muted or track.volume == 0)
        ]

        if len(muted_tracks):
            output["muted tracks"] = [repr(t) for t in muted_tracks]

        output["active tracks"] = len(list(Song.simple_tracks())) - len(muted_tracks)  # type: ignore[assignment]

        return output
