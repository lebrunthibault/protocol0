from typing import List, Optional, Any, cast

import Live

from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device.DeviceChain import DeviceChain
from protocol0.domain.shared.utils.list import find_if
from protocol0.shared.observer.Observable import Observable


class RackDevice(Device, Observable):
    def __init__(self, *a: Any, **k: Any) -> None:
        super(RackDevice, self).__init__(*a, **k)
        self._device: Live.RackDevice.RackDevice = cast(Live.RackDevice.RackDevice, self._device)
        self.chains: List[DeviceChain] = []
        self._view: Live.RackDevice.RackDevice.View = self._device.view
        # self._chains_listener.subject = self._device
        # self._chains_listener()

    def update(self, observable: Observable) -> None:
        if isinstance(observable, DeviceChain):
            self.notify_observers()

    def on_added(self) -> None:
        # show only one macro
        if not self.has_macro_mappings:
            self.remove_macro()
            self.remove_macro()
            self.remove_macro()
            self.remove_macro()

    @property
    def is_showing_chain_devices(self) -> bool:
        return not self._device.view.is_showing_chain_devices

    @is_showing_chain_devices.setter
    def is_showing_chain_devices(self, is_showing_chains: bool) -> None:
        self._view.is_showing_chain_devices = is_showing_chains

    @property
    def selected_chain(self) -> Optional[DeviceChain]:
        return find_if(lambda c: c._chain == self._view.selected_chain, self.chains)

    @selected_chain.setter
    def selected_chain(self, selected_chain: DeviceChain) -> None:
        self._view.selected_chain = selected_chain._chain

    @property
    def has_macro_mappings(self) -> bool:
        return self._device and self._device.has_macro_mappings and self.macros_count != 0

    @property
    def macros_count(self) -> int:
        return len(list(filter(lambda m: m, self._device.macros_mapped)))

    def remove_macro(self) -> None:
        try:
            if self._device:
                self._device.remove_macro()
        except RuntimeError:
            pass

    def disconnect(self) -> None:
        super(RackDevice, self).disconnect()
        for chain in self.chains:
            chain.disconnect()
