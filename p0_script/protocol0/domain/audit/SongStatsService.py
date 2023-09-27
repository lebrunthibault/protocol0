import json

from protocol0.domain.lom.set.AbletonSet import AbletonSet
from protocol0.domain.audit.stats.SceneStats import SceneStats
from protocol0.domain.audit.stats.SongStats import SongStats
from protocol0.domain.audit.utils import tail_logs
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.shared.logging.Logger import Logger


class SongStatsService(object):
    def __init__(self, ableton_set: AbletonSet):
        self._ableton_set = ableton_set

    @tail_logs
    def display_song_stats(self) -> None:
        stats = SongStats()
        Logger.clear()
        Logger.info(json.dumps(stats.to_dict(), indent=4))

    def export_song_structure(self) -> None:
        scene_stats = SceneStats()
        from protocol0.shared.logging.Logger import Logger
        Logger.dev(scene_stats.to_dict())
        Logger.dev(scene_stats.to_full_dict())
        Backend.client().post_scene_stats(scene_stats.to_full_dict())
