import collections

from typing import Dict, Any

from protocol0.domain.lom.scene.Scene import Scene
from protocol0.domain.shared.utils.utils import get_minutes_legend
from protocol0.shared.Song import Song


class SceneStat(object):
    def __init__(self, scene: Scene, start_bar_length: int) -> None:
        beat_duration = float(60) / Song.tempo()

        self._name = scene.name
        self._start_time = start_bar_length * Song.signature_numerator() * beat_duration
        self._end_time = (start_bar_length + scene.bar_length) * Song.signature_numerator() * beat_duration

        excluded_track_names = ("usamo", "auto")
        self._track_names = [track.full_name for track in scene.abstract_tracks if track.name.lower() not in excluded_track_names]

    def to_dict(self) -> Dict:
        output: Dict[str, Any] = collections.OrderedDict()
        output["name"] = self._name
        output["start_time"] = self._start_time
        output["end_time"] = self._end_time
        output["track_names"] = self._track_names

        return output

class SceneStats(object):
    def __init__(self) -> None:
        beat_duration = float(60) / Song.tempo()

        current_bar_length = 0
        scenes_stats = []

        for scene in Song.active_scenes():
            scenes_stats.append(SceneStat(scene, current_bar_length))
            current_bar_length += scene.bar_length

        self.scenes_stats = scenes_stats
        self.count = len(Song.active_scenes())
        self.bar_length = current_bar_length
        self.total_duration = current_bar_length * Song.signature_numerator() * beat_duration

    def to_dict(self) -> Dict:
        output: Dict[str, Any] = collections.OrderedDict()
        output["count"] = self.count
        output["total duration"] = get_minutes_legend(self.total_duration)

        return output

    def to_full_dict(self) -> Dict:
        output = self.to_dict()
        output["scenes"] = [scene_stat.to_dict() for scene_stat in self.scenes_stats]

        return output
