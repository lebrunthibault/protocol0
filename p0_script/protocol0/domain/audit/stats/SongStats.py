import collections

from typing import Dict, List

from protocol0.domain.audit.stats.DeviceStats import DevicesStats
from protocol0.domain.audit.stats.SceneStats import SceneStats
from protocol0.domain.audit.stats.Stats import Stats
from protocol0.domain.audit.stats.TrackStats import TrackStats


class SongStats(object):
    def __init__(self) -> None:
        self._stats: List[Stats] = [
            # ClipStats(),
            TrackStats(),
            DevicesStats(),
            SceneStats(),
        ]

    def to_dict(self) -> Dict:
        output = collections.OrderedDict()
        for stat in self._stats:
            title = stat.__class__.__name__.replace("Stats", "").lower()
            if not title.endswith("s"):
                title += "s"
            output[title] = stat.to_dict()

        return output
