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
        out = "DeviceChain(name=%s" % smart_string(self.name)
        if len(self.devices):
            out += ", first_device=%s" % self.devices[0]

        return out + ")"

    @property
    def name(self) -> str:
        return self._chain.name

    @subject_slot("devices")
    def _devices_listener(self) -> None:
        from protocol0.domain.lom.device.Device import Device

        self.devices = [Device.make(device) for device in self._chain.devices]
        self.notify_observers()

    def disconnect(self) -> None:
        super(DeviceChain, self).disconnect()
        for device in self.devices:
            device.disconnect()
