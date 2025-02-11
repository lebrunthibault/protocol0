from itertools import chain
from typing import List, Optional, Iterator, cast, Dict

import Live
from _Framework.SubjectSlot import subject_slot, SlotManager

from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device.DeviceChain import DeviceChain
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.device.MixerDevice import MixerDevice
from protocol0.domain.lom.device.RackDevice import RackDevice
from protocol0.domain.lom.device_parameter.DeviceParameter import DeviceParameter
from protocol0.domain.shared.LiveObjectMapping import LiveObjectMapping
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils.list import find_if
from protocol0.shared.observer.Observable import Observable

DeviceWithChainMapping = Dict[Device, Optional[DeviceChain]]


class SimpleTrackDevices(SlotManager):
    def __init__(self, live_track: Live.Track.Track) -> None:
        super(SimpleTrackDevices, self).__init__()
        self._track = live_track
        self._devices: List[Device] = []
        self._all_devices: DeviceWithChainMapping = {}
        self._devices_listener.subject = live_track
        self._devices_mapping = LiveObjectMapping(Device.make)
        self.mixer_device = MixerDevice(live_track.mixer_device)

    def __repr__(self) -> str:
        return "SimpleTrackDevices(%s)" % self._track.name

    def __iter__(self) -> Iterator[Device]:
        return iter(self._devices)

    def update(self, observable: Observable) -> None:
        if isinstance(observable, RackDevice):
            self.build()

    def build(self) -> None:
        self._devices_listener()

    @subject_slot("devices")
    def _devices_listener(self) -> None:
        for device in self._devices:
            device.disconnect()

        self._devices_mapping.build(self._track.devices)
        for added_device in self._devices_mapping.added:
            Scheduler.defer(added_device.on_added)  # type: ignore[attr-defined]
        self._devices = cast(List[Device], self._devices_mapping.all)
        self._all_devices = self._find_all_devices(self._devices)

        # for device in self.all:
        #     if isinstance(device, RackDevice):
        #         device.register_observer(self)

        # self.notify_observers()

    @property
    def all(self) -> List[Device]:
        return list(self._all_devices.keys())

    @property
    def all_devices_with_chain(self) -> DeviceWithChainMapping:
        return self._all_devices

    @property
    def selected(self) -> Optional[Device]:
        if self._track and self._track.view.selected_device:
            device: Optional[Device] = find_if(
                lambda d: d._device == self._track.view.selected_device, self.all
            )
            if device is None:
                raise Protocol0Warning(
                    "%s is not in %s devices"
                    % (
                        self._track.view.selected_device.name,
                        self._track.name,
                    )
                )
            return device
        else:
            return None

    @property
    def has_instrument(self) -> bool:
        return any(d.is_instrument for d in self)

    @property
    def first(self) -> Optional[Device]:
        return self._devices[0] if self._devices else None

    @property
    def last(self) -> Optional[Device]:
        return self._devices[-1] if self._devices else None

    @property
    def prev(self) -> Optional[Device]:
        return self._get_sibling(False)

    @property
    def next(self) -> Optional[Device]:
        return self._get_sibling(True)

    def _get_sibling(self, go_next: bool) -> Optional[Device]:
        if not self._devices:
            return None

        if not self.selected:
            return self._devices[0]

        # do not loop over list
        if (
            go_next
            and self.selected == self._devices[-1]
            or not go_next
            and self.selected == self._devices[0]
        ):
            return self.selected

        selected_index = self._devices.index(self.selected)
        try:
            return self._devices[selected_index + (1 if go_next else -1)]
        except IndexError:
            return self._devices[0]

    def get_one_from_enum(
        self, device_enum: DeviceEnum, all_devices: bool = False, enabled: bool = False
    ) -> Optional[Device]:
        if all_devices:
            devices = self.all
        else:
            devices = self._devices

        if enabled:
            devices = [d for d in devices if d.is_enabled]

        return find_if(device_enum.matches, devices)

    def _find_all_devices(
        self, devices: Optional[List[Device]], only_visible: bool = False
    ) -> DeviceWithChainMapping:
        """Returns a list with all devices from a track or chain"""
        all_devices: DeviceWithChainMapping = {}
        if devices is None:
            return {}
        for device in filter(None, devices):  # type: Device
            all_devices[device] = None

            if not isinstance(device, RackDevice):
                continue

            if device.can_have_drum_pads and device.can_have_chains and device.selected_chain:
                chains = [device.selected_chain]
            else:
                chains = device.chains

            for device_chain in chains:
                for chain_device in self._find_all_devices(
                    device_chain.devices, only_visible=only_visible
                ):
                    all_devices[chain_device] = device_chain

        return all_devices

    def get_device_or_rack_device(self, device: Device) -> Optional[RackDevice]:
        for rack_device in self.all:
            if not isinstance(rack_device, RackDevice):
                continue

            for device_chain in rack_device.chains:
                for chain_device in device_chain.devices:
                    if chain_device == device:
                        return self.get_device_or_rack_device(rack_device)

        if isinstance(device, RackDevice):
            return device
        else:
            return None

    def delete(self, device: Device) -> None:
        if device not in self.all:
            return None

        device_chain = self.all_devices_with_chain[device]

        if device_chain:
            device_chain.delete_device(device_chain.devices.index(device))
        else:
            device_index = self._devices.index(device)
            self._track.delete_device(device_index)  # noqa

        self.build()

        return None

    @property
    def parameters(self) -> List[DeviceParameter]:
        return (
            list(chain(*[device.parameters for device in self.all])) + self.mixer_device.parameters
        )

    @property
    def load_time(self) -> int:
        return sum(d.enum.load_time for d in self if d.enum is not None)

    def disconnect(self) -> None:
        super(SimpleTrackDevices, self).disconnect()
        for device in self.all:
            device.disconnect()
