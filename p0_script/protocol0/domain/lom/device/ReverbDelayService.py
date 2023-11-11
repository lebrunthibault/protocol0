from typing import List

from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.device_parameter.DeviceParamEnum import DeviceParamEnum
from protocol0.domain.lom.track.TrackAutomationService import is_param_automated
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger


def scroll_insert_device_volumes(device_enum: DeviceEnum, go_next: bool) -> None:
    return scroll_devices_param(device_enum, [DeviceParamEnum.WET, DeviceParamEnum.INPUT], go_next)


def scroll_devices_param(
    device_enum: DeviceEnum, param_enums: List[DeviceParamEnum], go_next: bool
) -> None:
    automated_tracks: List[SimpleTrack] = []

    def scroll_device(t: SimpleTrack, enums: List[DeviceParamEnum]) -> bool:
        for param_enum in enums:
            param = device.get_parameter_by_name(param_enum)
            if not param:
                Logger.warning(f"Couldn't find {param_enum} on {device_enum} on {t}")
                return False

            if not is_param_automated(track, param):
                param.scroll(go_next)
                return True

        return False

    for track in Song.simple_tracks():
        for device in [d for d in track.devices.all if d.enum == device_enum]:
            if not scroll_device(track, param_enums):
                automated_tracks.append(track)

    if len(automated_tracks):
        Logger.warning(
            f"Couldn't scroll {device_enum} on tracks:\n- "
            + "\n- ".join([t.name for t in automated_tracks])
        )
