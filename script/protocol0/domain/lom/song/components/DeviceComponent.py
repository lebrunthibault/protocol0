from functools import partial
from typing import Optional

import Live
from _Framework.SubjectSlot import SlotManager

from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device_parameter.DeviceParameter import DeviceParameter
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.ApplicationView import ApplicationView
from protocol0.domain.shared.utils.list import find_if
from protocol0.shared.Song import Song
from protocol0.shared.sequence.Sequence import Sequence


class DeviceComponent(SlotManager):
    def __init__(self, song_view: Live.Song.Song.View) -> None:
        super(DeviceComponent, self).__init__()
        self._view = song_view

    @property
    def selected_parameter(self) -> Optional[DeviceParameter]:
        return find_if(
            lambda p: p._device_parameter == self._view.selected_parameter,
            Song.selected_track().devices.parameters,
        )

    def select_device(self, track: SimpleTrack, device: Device) -> Sequence:
        seq = Sequence()
        seq.add(track.select)
        seq.add(partial(self._view.select_device, device._device))
        seq.add(ApplicationView.focus_detail)
        seq.add(ApplicationView.show_device)
        seq.add(ApplicationView.focus_device)

        return seq.done()
