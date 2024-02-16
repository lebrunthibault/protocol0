from typing import Optional, Set, List

from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device_parameter.DeviceParameter import DeviceParameter
from protocol0.domain.lom.track.group_track.NormalGroupTrack import NormalGroupTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import route_track_to_bus, SimpleTrack
from protocol0.domain.lom.track.simple_track.audio.special.SimpleAutomationTrack import (
    SimpleAutomationTrack,
)
from protocol0.shared.Song import Song
from protocol0.shared.sequence.Sequence import Sequence


def get_all_automated_parameters(track: SimpleTrack, device: Device) -> Set[DeviceParameter]:
    automated_parameters = set()
    for clip in track.clips:
        automated_parameters.update(
            set(clip.automation.get_automated_parameters(device.parameters))
        )

    return automated_parameters


class MixBusesTrack(NormalGroupTrack):
    TRACK_NAME = "*"

    def on_tracks_change(self) -> None:
        super(MixBusesTrack, self).on_tracks_change()

        for track in self.sub_tracks:
            for device in track.base_track.devices.all:
                device.automated_params = get_all_automated_parameters(track.base_track, device)

    def on_added(self) -> Optional[Sequence]:
        super(MixBusesTrack, self).on_added()

        for track in Song.simple_tracks():
            if track != self.base_track and track not in self.sub_tracks:
                route_track_to_bus(track)

        return None

    def reset_bus_tracks_automation(self) -> None:
        buses_track = [t for t in self.sub_tracks if isinstance(t, SimpleAutomationTrack)]

        for track in buses_track:
            if not track.clips:
                continue

            if track not in Song.selected_scene().abstract_tracks:
                automated_params: List[DeviceParameter] = []

                for device in track.devices:
                    automated_params += device.automated_params

                for param in automated_params:
                    param.reset()
