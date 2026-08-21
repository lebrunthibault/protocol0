"""Device actions over the addressing grammar.

Devices are targeted by a track spec (`track`, default SEL) plus a device spec
(`device`, default SEL = the track's selected device): 1-based top-level index,
a dotted rack path "1.2.3" (3rd device of the 2nd chain of the 1st rack), or a
name matched over all devices including rack chains.
"""
from protocol0.application.http.HttpServer import get_container
from protocol0.application.plugin.PluginInterface import PluginInterface
from protocol0.application.plugin.action import action
from protocol0.domain.lom.addressing.device import resolve_device
from protocol0.domain.lom.addressing.parameter import resolve_parameter
from protocol0.domain.lom.addressing.track import resolve_track
from protocol0.domain.lom.addressing.values import resolve_bool, resolve_continuous
from protocol0.domain.lom.device.DeviceService import DeviceService
from protocol0.domain.lom.song.components.DeviceComponent import DeviceComponent
from protocol0.shared.sequence.Sequence import Sequence


class DevicePlugin(PluginInterface):
    name = "device"

    @action
    def load_device(self, name: str) -> Sequence:
        """Load a device (instrument or audio effect) onto the selected track by name."""
        # Returned so ``@action`` closes the undo step only once the device is loaded.
        return get_container().get(DeviceService).load_device(name)

    @action
    def select(self, track: str = "SEL", device: str = "SEL") -> Sequence:
        """Select a device and show it (device: SEL, index, "1.2.3" rack path, name)."""
        target_track = resolve_track(track)
        target_device = resolve_device(target_track, device)
        return get_container().get(DeviceComponent).select_device(target_track, target_device)

    @action
    def toggle(self, track: str = "SEL", device: str = "SEL", value: str = "TGL") -> None:
        """Turn a device on or off (value: ON, OFF or TGL)."""
        target = resolve_device(resolve_track(track), device)
        target.is_enabled = resolve_bool(value, target.is_enabled)

    @action
    def delete(self, track: str = "SEL", device: str = "SEL") -> None:
        """Delete a device (works inside rack chains too)."""
        target_track = resolve_track(track)
        target_track.devices.delete(resolve_device(target_track, device))

    @action
    def set_parameter(
        self, parameter: str, value: str, track: str = "SEL", device: str = "SEL"
    ) -> None:
        """Set a device parameter (parameter: 1-based index or name; value:
        absolute, x%, < / > steps, RND or RESET)."""
        target = resolve_device(resolve_track(track), device)
        target_parameter = resolve_parameter(target, parameter)
        target_parameter.value = resolve_continuous(
            value,
            target_parameter.value,
            target_parameter.min,
            target_parameter.max,
            default=target_parameter.default_value,
        )
