from protocol0.domain.lom.device_parameter.DeviceParamEnum import DeviceParamEnum
from protocol0.domain.lom.track.CurrentMonitoringStateEnum import CurrentMonitoringStateEnum
from protocol0.domain.lom.track.group_track.NormalGroupTrack import NormalGroupTrack
from protocol0.domain.lom.track.routing.OutputRoutingTypeEnum import OutputRoutingTypeEnum
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger


class MixingService(object):
    def scroll_all_tracks_volume(self, go_next: bool) -> None:
        for track in Song.abstract_tracks():
            try:
                if isinstance(track, NormalGroupTrack) or (
                    isinstance(track, SimpleAudioTrack)
                    and track.current_monitoring_state == CurrentMonitoringStateEnum.IN
                ):
                    continue
            except RuntimeError:
                continue

            track.base_track.scroll_volume(go_next)

    def log_state(self) -> None:
        def is_zero_volume(t: SimpleTrack) -> bool:
            return not t.is_foldable and t.volume < -45

        def routed_to_master(t: SimpleTrack) -> bool:
            return t.output_routing.type == OutputRoutingTypeEnum.MASTER

        Logger.info(f"zero_volume_tracks: {list(filter(is_zero_volume, Song.simple_tracks()))}")
        Logger.info(f"routed to master: {list(filter(routed_to_master, Song.simple_tracks()))}")

    def toggle_adptr_stereo_mode(self, stereo_mode: str) -> None:
        adptr = Song.master_track().adptr

        if not adptr:
            return None

        stereo_mode_param = adptr.get_parameter_by_name(DeviceParamEnum.STEREO_MODE)

        if not stereo_mode_param:
            return None

        stereo_mode_to_value = {
            "stereo": 0,
            "mono": 0.3,
            "sides": 1,
        }

        value = stereo_mode_to_value[stereo_mode]

        if stereo_mode_param.value == value:
            stereo_mode_param.value = stereo_mode_to_value["stereo"]
        else:
            stereo_mode_param.value = value
