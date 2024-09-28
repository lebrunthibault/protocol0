from functools import partial
from typing import Optional, Tuple, List

from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.ApplicationView import ApplicationView
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.shared.sequence.Sequence import Sequence
from protocol0.shared.types import Coords


class DeviceDisplayService(object):
    def toggle_plugin_window(self, track: SimpleTrack, device: Device) -> Optional[Sequence]:
        if device.enum is None:
            return None

        seq = Sequence()
        seq.add(ApplicationView.show_device)
        seq.defer()

        devices_to_collapse = [d for d in track.devices if not d.is_collapsed]
        for d in devices_to_collapse:
            d.is_collapsed = True

        device_coords = self._get_device_show_button_click_coordinates(track, device)

        seq.defer()
        seq.add(partial(self._toggle_ableton_button, device_coords))
        seq.wait(30)
        seq.add(partial(self._un_collapse_devices, devices_to_collapse))

        return seq.done()

    def _toggle_ableton_button(self, coords: Coords) -> Sequence:
        x, y = coords

        seq = Sequence()
        seq.add(partial(Backend.client().toggle_ableton_button, x=x, y=y))
        seq.wait_for_backend_event("button_toggled")

        return seq.done()

    def _un_collapse_devices(self, devices_to_un_collapse: List[Device]) -> None:
        for d in devices_to_un_collapse:
            d.is_collapsed = False

    def _get_device_show_button_click_coordinates(
        self, track: SimpleTrack, device: Device
    ) -> Tuple[int, int]:
        device_position = list(track.devices).index(device) + 1
        x = device_position * 38 + 4

        return (
            x - 3,
            970 - 2,
        )  # we click not exactly in the center so as to know if the button is activated or not
