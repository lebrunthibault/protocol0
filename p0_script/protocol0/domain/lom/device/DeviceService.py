from functools import partial
from typing import Optional, cast, Callable

import Live

from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device.DeviceChain import DeviceChain
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.device.DryWetDeviceAddedEvent import DryWetDeviceAddedEvent
from protocol0.domain.lom.device.RackDevice import RackDevice
from protocol0.domain.lom.song.components.DeviceComponent import DeviceComponent
from protocol0.domain.lom.song.components.TrackCrudComponent import TrackCrudComponent
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.lom.track.simple_track.midi.SimpleMidiTrack import SimpleMidiTrack
from protocol0.domain.shared.BrowserServiceInterface import BrowserServiceInterface
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.shared.Song import Song
from protocol0.shared.Undo import Undo
from protocol0.shared.logging.StatusBar import StatusBar
from protocol0.shared.sequence.Sequence import Sequence


def find_parent_rack(track: SimpleTrack, device: Device) -> Optional[RackDevice]:
    if device in track.devices:
        return None

    for rack_device in [d for d in track.devices if isinstance(d, RackDevice)]:
        for chain in rack_device.chains:
            if device in chain.devices:
                return rack_device

    raise Protocol0Error("Couldn't find device %s (may be too nested to be detected)" % device.name)


def _switch_master_cpu_devices() -> bool:
    god_particle = Song.master_track().god_particle

    # switch god particle
    if not god_particle:
        return False

    god_particle_rack = find_parent_rack(Song.master_track(), god_particle)

    if god_particle_rack:
        god_particle = god_particle_rack

    try:
        master_devices = list(Song.master_track().devices)
        next_device: Device = master_devices[master_devices.index(god_particle) + 1]
    except IndexError:
        return False

    if (
        next_device.enum != DeviceEnum.L2_LIMITER and not isinstance(next_device, RackDevice)
    ) or next_device.is_enabled == god_particle.is_enabled:
        return False

    next_device.toggle()
    god_particle.toggle()

    return True


class DeviceService(object):
    def __init__(
        self,
        track_crud_component: TrackCrudComponent,
        device_component: DeviceComponent,
        browser_service: BrowserServiceInterface,
        move_device: Callable,
    ) -> None:
        self._track_crud_component = track_crud_component
        self._device_component = device_component
        self._browser_service = browser_service
        self._move_device = move_device

        DomainEventBus.subscribe(DryWetDeviceAddedEvent, self._on_dry_wet_device_added_event)

    def load_device(self, enum_name: str, create_track: bool = False) -> Sequence:
        Undo.begin_undo_step()

        device_enum = DeviceEnum[enum_name]
        track = Song.selected_track()

        self._select_track_and_device(device_enum)

        seq = Sequence()

        if device_enum == DeviceEnum.SPLICE_BRIDGE and Song.splice_track():
            Song.splice_track().delete()

        if device_enum.is_instrument:
            # reuse empty midi tracks
            if create_track and not (
                isinstance(Song.selected_track(), SimpleMidiTrack)
                and not Song.selected_track().devices.has_instrument
            ):
                seq.add(self._track_crud_component.create_midi_track)

            elif track.instrument:
                instrument_device = track.instrument_rack_device or track.instrument.device
                if instrument_device:
                    track.devices.delete(instrument_device)

        def rename_default_midi_track() -> None:
            if Song.selected_track().lower_name == "midi" and device_enum.is_instrument:
                Song.selected_track().name = device_enum.track_name
                if device_enum.track_color:
                    Song.selected_track().color = device_enum.track_color

        seq.defer()
        seq.add(rename_default_midi_track)

        seq.add(partial(self._browser_service.load_device_from_enum, device_enum))

        if device_enum.is_rack_preset:
            seq.add(self.toggle_selected_rack_chain)

        seq.add(Undo.end_undo_step)
        return seq.done()

    def _select_track_and_device(self, device_enum: DeviceEnum) -> None:
        track = Song.selected_track()

        if device_enum.is_instrument:
            track.select()
            return

        if Song.selected_device():
            track.device_insert_mode = Live.Track.DeviceInsertMode.selected_right
            return None

        device_to_select = self._get_device_to_select_for_insertion(track, device_enum)
        if device_to_select:
            track.device_insert_mode = Live.Track.DeviceInsertMode.selected_right
            self._device_component.select_device(track, device_to_select)

        else:
            track.device_insert_mode = Live.Track.DeviceInsertMode.selected_right
            if len(list(track.devices)) > 0:
                self._device_component.select_device(track, list(track.devices)[-1])

    def move_device(self, device: Device, chain: DeviceChain, position: int) -> Sequence:
        self._move_device(device._device, chain._chain, position)
        chain._devices_listener()  # workaround as chain devices listener doesn't seem to be called
        return Sequence().defer().done()

    def _on_dry_wet_device_added_event(self, _: DryWetDeviceAddedEvent) -> None:
        dry_wet_device = Song.selected_device()
        if not isinstance(dry_wet_device, RackDevice):
            return None

        devices = list(Song.selected_track().devices)
        try:
            next_device = devices[devices.index(dry_wet_device) + 1]
        except IndexError:
            return

        self.move_device(next_device, dry_wet_device.chains[1], 0)

    def _get_device_to_select_for_insertion(
        self, track: SimpleTrack, device_enum: DeviceEnum
    ) -> Optional[Device]:
        if len(list(track.devices)) == 0:
            return None

        for device in track.devices:
            if not device.enum or device.is_instrument or device.is_midi:
                continue

            if device.enum.device_group_position >= device_enum.device_group_position:
                return device

        return None

    def toggle_selected_rack_chain(self) -> None:
        device = Song.selected_device()
        assert device, "No selected device"

        def is_valid_rack(d: Device) -> bool:
            return (
                isinstance(d, RackDevice) and len(d.chains) == 2 and len(d.chains[1].devices) != 0
            )

        if not is_valid_rack(device):
            parent_rack = find_parent_rack(Song.selected_track(), device)

            if parent_rack and is_valid_rack(parent_rack):
                parent_rack.is_showing_chain_devices = False
                self._device_component.select_device(Song.selected_track(), parent_rack)
                return None

            StatusBar.show_message("not a valid rack device")
            return None

        device = cast(RackDevice, device)

        device.is_showing_chain_devices = True
        device.selected_chain = device.chains[1]

        self._device_component.select_device(Song.selected_track(), device.chains[1].devices[-1])

    def toggle_cpu_heavy_devices(self) -> None:
        toggle_cpu_heavy = bool(
            Song.master_track().god_particle and not Song.master_track().god_particle.is_enabled
        )

        master_handled = _switch_master_cpu_devices()

        if not master_handled:
            Backend.client().show_warning("Master devices not set up properly")
            return None

        drums_track = Song.drums_track()
        if drums_track:
            shadow_hills = drums_track.devices.get_one_from_enum(DeviceEnum.SHADOW_HILLS_COMP)
            if shadow_hills:
                shadow_hills.is_enabled = toggle_cpu_heavy
            black_box = drums_track.devices.get_one_from_enum(DeviceEnum.BLACK_BOX)
            if black_box:
                black_box.is_enabled = toggle_cpu_heavy

        if toggle_cpu_heavy:
            StatusBar.show_message("High CPU enabled")
        else:
            StatusBar.show_message("Low CPU enabled")
