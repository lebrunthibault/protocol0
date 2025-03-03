from typing import Dict, List

from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device_parameter.DeviceParamEnum import DeviceParamEnum
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.shared.Song import Song
from protocol0.shared.Undo import Undo

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
