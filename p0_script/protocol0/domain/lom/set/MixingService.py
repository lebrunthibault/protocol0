from typing import Dict, List

from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device_parameter.DeviceParamEnum import DeviceParamEnum
from protocol0.domain.lom.track.CurrentMonitoringStateEnum import CurrentMonitoringStateEnum
from protocol0.domain.lom.track.group_track.NormalGroupTrack import NormalGroupTrack
from protocol0.domain.lom.track.routing.OutputRoutingTypeEnum import OutputRoutingTypeEnum
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.shared.Song import Song
from protocol0.shared.Undo import Undo
from protocol0.shared.logging.Logger import Logger

SimpleTrackToDevices = Dict[SimpleTrack, List[Device]]


def balance_bus_levels_to_zero(track: SimpleTrack) -> SimpleTrackToDevices:
    assert track.is_foldable, "Expected bus or master track"

    bus_volume = track.volume
    Undo.begin_undo_step()

    for sub_track in track.sub_tracks:
        if sub_track.volume + bus_volume > 6:
            raise Protocol0Error(f"{sub_track.name} is too hot")

    bus_compressors: SimpleTrackToDevices = {}
    compressors = [device for device in track.devices if device.enum and device.enum.is_compressor]
    if compressors:
        bus_compressors[track] = compressors

    track.volume = 0

    for sub_track in track.sub_tracks:
        sub_track.volume += bus_volume

        if sub_track.volume > 0 and sub_track.is_foldable:
            bus_compressors = {**bus_compressors, **balance_bus_levels_to_zero(sub_track)}

    Undo.end_undo_step()

    return bus_compressors


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
