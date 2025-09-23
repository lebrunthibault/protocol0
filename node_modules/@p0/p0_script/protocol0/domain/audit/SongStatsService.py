import json

from protocol0.domain.audit.stats.SceneStats import SceneStats
from protocol0.domain.audit.stats.SongStats import SongStats
from protocol0.domain.audit.utils import tail_logs
from protocol0.domain.lom.set.AbletonSet import AbletonSet
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.logging.StatusBar import StatusBar


class SongStatsService(object):
    def __init__(self, ableton_set: AbletonSet):
        self._ableton_set = ableton_set

    @tail_logs
    def display_song_stats(self) -> None:
        stats = SongStats()
        Logger.clear()
        Logger.info(json.dumps(stats.to_dict(), indent=4))

    def get_song_structure(self) -> SceneStats:
        scene_names = [scene.scene_name.get_base_name() for scene in Song.scenes()]
        if "" in scene_names:
            scene_names.remove("")

        if len(scene_names) > 2 and len(list(set(scene_names))) < 2:
            StatusBar.show_message("Scenes are not named")

        return SceneStats()
