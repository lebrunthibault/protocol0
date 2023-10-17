import Live
from _Framework.SubjectSlot import subject_slot
from typing import List, Optional, Any, cast

from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device.DeviceChain import DeviceChain
from protocol0.domain.shared.utils.list import find_if
from protocol0.shared.observer.Observable import Observable


class RackDevice(Device, Observable):
    def __init__(self, *a: Any, **k: Any) -> None:
        super(RackDevice, self).__init__(*a, **k)
        self._device: Live.RackDevice.RackDevice = cast(
            Live.RackDevice.RackDevice, self._device
        )
        self.chains: List[DeviceChain] = []
        self._view: Live.RackDevice.RackDevice.View = self._device.view
        self._chains_listener.subject = self._device
        self._chains_listener()

    def update(self, observable: Observable) -> None:
        if isinstance(observable, DeviceChain):
            self.notify_observers()

    @subject_slot("chains")
    def _chains_listener(self) -> None:
        self.chains = [DeviceChain(chain, index) for index, chain in enumerate(self._device.chains)]

        for chain in self.chains:
            chain.register_observer(self)

    @property
    def selected_chain(self) -> Optional[DeviceChain]:
        return find_if(lambda c: c._chain == self._view.selected_chain, self.chains)

    @selected_chain.setter
    def selected_chain(self, selected_chain: DeviceChain) -> None:
        self._view.selected_chain = selected_chain._chain

    @property
    def variation_count(self) -> int:
        return self._device.variation_count

    @property
    def selected_variation_index(self) -> int:
        return self._device.selected_variation_index

    @selected_variation_index.setter
    def selected_variation_index(self, selected_variation_index: int) -> None:
        if selected_variation_index < 0:
            return

        self._device.selected_variation_index = selected_variation_index
        self._device.recall_selected_variation()

    def increment_variation(self) -> None:
        if self.selected_variation_index < 0:
            self.selected_variation_index = 0

        if self.selected_variation_index < self.variation_count - 1:
            self.selected_variation_index += 1

        self.notify_observers()

    def decrement_variation(self) -> None:
        if self.selected_variation_index < 0:
            self.selected_variation_index = 0
        else:
            self.selected_variation_index -= 1

        self.notify_observers()

    def disconnect(self) -> None:
        super(RackDevice, self).disconnect()
        for chain in self.chains:
            chain.disconnect()
