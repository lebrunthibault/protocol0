from typing import Optional, List

from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.device_parameter.DeviceParamEnum import DeviceParamEnum
from protocol0.infra.interface.BrowserService import BrowserService
from protocol0.shared.Song import Song
from protocol0.shared.sequence.Sequence import Sequence


def _get_all_track_clippers() -> List[Device]:
    clippers = []

    for track in Song.simple_tracks():
        if track.is_bus_track:
            continue

        clippers.append(track.devices.get_one_from_enum(DeviceEnum.STANDARD_CLIP))

    return list(filter(None, clippers))


class ClipperService:
    def __init__(self, browser_service: BrowserService):
        self._browser_service = browser_service

    def toggle(self) -> Optional[Sequence]:
        clipper = Song.selected_track().devices.get_one_from_enum(DeviceEnum.STANDARD_CLIP)
        if not clipper:
            return self._browser_service.load_device_from_enum(DeviceEnum.STANDARD_CLIP)

        # clipper.toggle()

        # input_gain = clipper.get_parameter_by_name(DeviceParamEnum.INPUT_GAIN)
        # output_gain = clipper.get_parameter_by_name(DeviceParamEnum.OUTPUT_GAIN)

        return None

    def scroll(self, go_next: bool) -> Optional[Sequence]:
        clipper = Song.selected_track().devices.get_one_from_enum(DeviceEnum.STANDARD_CLIP)
        if not clipper:
            return self._browser_service.load_device_from_enum(DeviceEnum.STANDARD_CLIP)

        clipper.is_enabled = True
        input_gain = clipper.get_parameter_by_name(DeviceParamEnum.INPUT_GAIN)
        output_gain = clipper.get_parameter_by_name(DeviceParamEnum.OUTPUT_GAIN)

        input_gain.scroll(go_next)
        output_gain.scroll(not go_next)

        return None

    def toggle_all(self) -> None:
        for clipper in _get_all_track_clippers():
            clipper.toggle()

    def scroll_all(self, go_next: bool) -> None:
        for clipper in _get_all_track_clippers():
            clipper.get_parameter_by_name(DeviceParamEnum.INPUT_GAIN).scroll(go_next, steps=3000)
