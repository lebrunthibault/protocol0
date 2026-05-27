import Live
from _Framework.SubjectSlot import subject_slot, SlotManager
from typing import List

from protocol0.domain.shared.utils.string import smart_string
from protocol0.shared.observer.Observable import Observable


class DeviceChain(SlotManager, Observable):
    def __init__(self, chain: Live.Chain.Chain, index: int) -> None:
        super(DeviceChain, self).__init__()
        self._chain = chain
        self.index = index
        from protocol0.domain.lom.device.Device import Device

        self.devices: List[Device] = []
        self._devices_listener.subject = self._chain
        self._devices_listener()

    def __repr__(self) -> str:
        return f"DeviceChain(name={smart_string(self.name)})"

    @property
    def name(self) -> str:
        return self._chain.name

    @subject_slot("devices")
    def _devices_listener(self) -> None:
        """NB: This listener seems broken and should be called manually"""
        from protocol0.domain.lom.device.Device import Device

        self.devices = [Device.make(device) for device in self._chain.devices]
        self.notify_observers()

    def delete_device(self, device_index: int) -> None:
        self._chain.delete_device(device_index)
        self._devices_listener()

    def disconnect(self) -> None:
        super(DeviceChain, self).disconnect()
        for device in self.devices:
            device.disconnect()
