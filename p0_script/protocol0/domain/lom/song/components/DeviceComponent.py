from functools import partial
from typing import Optional

import Live
from _Framework.SubjectSlot import subject_slot, SlotManager

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

        self._selected_parameter_listener.subject = self._view

        # this parameter is here to work around the fact that view.selected_parameter is not settable
        # it will make the getter return the parameter we want even though it is not
        # currently selected in the interface
        # for most uses it's enough and works as though we did view.selected_parameter = param
        self._overridden_selected_parameter: Optional[DeviceParameter] = None

    @subject_slot("selected_parameter")
    def _selected_parameter_listener(self) -> None:
        """Reset the parameter"""
        self._overridden_selected_parameter = None

    @property
    def selected_parameter(self) -> Optional[DeviceParameter]:
        if self._overridden_selected_parameter is not None:
            return self._overridden_selected_parameter
        all_parameters = [
            param for track in Song.simple_tracks() for param in track.devices.parameters
        ]
        return find_if(
            lambda p: p._device_parameter == self._view.selected_parameter, all_parameters
        )

    @selected_parameter.setter
    def selected_parameter(self, parameter: Optional[DeviceParameter]) -> None:
        self._overridden_selected_parameter = parameter

    def select_device(self, track: SimpleTrack, device: Device) -> Sequence:
        seq = Sequence()
        seq.add(track.select)
        seq.add(partial(self._view.select_device, device._device))
        seq.add(ApplicationView.focus_detail)
        seq.add(ApplicationView.show_device)
        seq.add(ApplicationView.focus_device)

        return seq.done()
