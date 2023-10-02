from protocol0.domain.lom.track.CurrentMonitoringStateEnum import CurrentMonitoringStateEnum
from protocol0.domain.lom.track.group_track.NormalGroupTrack import NormalGroupTrack
from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack
from protocol0.shared.Song import Song


class MixingService(object):
    def scroll_all_tracks_volume(self, go_next: bool) -> None:
        for track in Song.abstract_tracks():
            if isinstance(track, NormalGroupTrack) or (
                isinstance(track, SimpleAudioTrack)
                and track.current_monitoring_state == CurrentMonitoringStateEnum.IN
            ):
                continue

            track.base_track.scroll_volume(go_next)
