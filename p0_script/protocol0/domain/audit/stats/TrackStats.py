import collections
from typing import Dict

from protocol0.domain.lom.track.group_track.NormalGroupTrack import NormalGroupTrack
from protocol0.domain.lom.track.group_track.ext_track.SimpleMidiExtTrack import SimpleMidiExtTrack
from protocol0.domain.lom.track.simple_track.midi.special.UsamoTrack import UsamoTrack
from protocol0.domain.shared.utils.list import find_if
from protocol0.shared.Config import Config
from protocol0.shared.Song import Song


class TrackStats(object):
    def __init__(self) -> None:
        excluded_track_classes = (NormalGroupTrack, UsamoTrack)
        tracks = [t for t in Song.abstract_tracks() if not isinstance(t, excluded_track_classes)]
        tracks_sorted = sorted(tracks, key=lambda track: track.load_time)
        self._slow_tracks = [t for t in list(reversed(tracks_sorted))[0:10] if t.load_time]

    def to_dict(self) -> Dict:
        output = collections.OrderedDict()
        output["slow tracks"] = ["%s: %s ms" % (t.name, t.load_time) for t in self._slow_tracks]

        tracks = list(Song.abstract_tracks())
        usamo_track = find_if(lambda t: isinstance(t, UsamoTrack), Song.simple_tracks())
        if usamo_track:
            tracks.remove(usamo_track)

            if usamo_track.group_track:
                tracks.remove(usamo_track.group_track.abstract_track)
                for sub_track in usamo_track.group_track.abstract_track.sub_tracks:
                    if sub_track in tracks:
                        tracks.remove(sub_track)

        muted_tracks = [
            track
            for track in Song.simple_tracks()
            if not track.is_foldable
            and not isinstance(track, (SimpleMidiExtTrack, UsamoTrack))
            and (
                all(clip.muted for clip in track.clips)
                or track.muted
                or track.volume == Config.ZERO_VOLUME_DB
                or any(t.muted for t in track.group_tracks)
            )
        ]

        if len(muted_tracks):
            output["muted tracks"] = [repr(t) for t in muted_tracks]

        simple_tracks = [t for t in tracks if not isinstance(t, NormalGroupTrack)]
        output["active tracks"] = len(simple_tracks) - len(muted_tracks)  # type: ignore[assignment]

        return output
