from functools import partial
from typing import Optional, cast, Callable

import Live

from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.device.DeviceLoadedEvent import DeviceLoadedEvent
from protocol0.domain.lom.device.DryWetDeviceAddedEvent import DryWetDeviceAddedEvent
from protocol0.domain.lom.device.RackDevice import RackDevice
from protocol0.domain.lom.song.components.DeviceComponent import DeviceComponent
from protocol0.domain.lom.song.components.TrackCrudComponent import TrackCrudComponent
from protocol0.domain.lom.track.group_track.ext_track.ExternalSynthTrack import ExternalSynthTrack
from protocol0.domain.lom.track.group_track.ext_track.SimpleMidiExtTrack import SimpleMidiExtTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.ApplicationView import ApplicationView
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
    god_particle = Song.master_track().devices.get_one_from_enum(DeviceEnum.GOD_PARTICLE)

    # switch god particle
    if not god_particle:
        return False

    try:
        master_devices = list(Song.master_track().devices)
        next_device: Device = master_devices[master_devices.index(god_particle) + 1]
    except IndexError:
        return False

    if next_device.enum != DeviceEnum.L2_LIMITER or next_device.is_enabled == god_particle.is_enabled:
        return False

    next_device.toggle()
    god_particle.toggle()

    return True

def _switch_black_box_devices():
    for track in Song.simple_tracks():
        black_box = track.devices.get_one_from_enum(DeviceEnum.BLACK_BOX)

        if not black_box:
            continue

        try:
            devices = list(track.devices)
            next_device: Device = devices[devices.index(black_box) + 1]
        except IndexError:
            Backend.client().show_warning(f"Blackbox not set up property on {track}")
            continue

        if next_device.enum in (DeviceEnum.SATURATOR, DeviceEnum.OVERDRIVE, DeviceEnum.DYNAMIC_TUBE) or next_device.is_enabled == black_box.is_enabled:
            Backend.client().show_warning(f"Blackbox not set up property on {track}")
            continue

        next_device.toggle()
        black_box.toggle()

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

        DomainEventBus.subscribe(DeviceLoadedEvent, self._on_device_loaded_event)
        DomainEventBus.subscribe(DryWetDeviceAddedEvent, self._on_dry_wet_device_added_event)

    def load_device(self, enum_name: str, create_track: bool = False) -> Sequence:
        Undo.begin_undo_step()
        device_enum = DeviceEnum[enum_name]
        track = Song.selected_track()
        is_clip_view_visible = ApplicationView.is_clip_view_visible()

        self._load_device_select_track(device_enum)

        seq = Sequence()

        if device_enum.is_instrument:
            if create_track and track.instrument:
                seq.add(self._track_crud_component.create_midi_track)
                seq.add(lambda: setattr(Song.selected_track(), "name", device_enum.track_name))

                # if selected track is empty, delete it to make some room
                # if len(track.clips) == 0 and not track.has_category(TrackCategoryEnum.BASS):
                #     seq.add(track.delete)
            elif track.instrument:
                instrument_device = track.instrument_rack_device or track.instrument.device
                if instrument_device:
                    track.devices.delete(instrument_device)

        seq.add(partial(self._browser_service.load_device_from_enum, device_enum))

        if (
            device_enum.default_parameter is not None
            and Song.selected_clip_slot() is not None
            and Song.selected_clip(raise_if_none=False) is not None
            and is_clip_view_visible
        ):
            seq.add(partial(self._show_default_automation, Song.selected_clip()))

        if device_enum.is_instrument and device_enum.instrument_enum == DeviceEnum.SYLENTH1:
            seq.add(Backend.client().un_group)

        seq.add(Undo.end_undo_step)
        return seq.done()

    def _get_instrument_track(self, device_enum: DeviceEnum) -> SimpleTrack:
        selected_track = Song.selected_track()
        current_track = Song.current_track()

        # only case when we want to select the midi track of an ext track
        if isinstance(selected_track, SimpleMidiExtTrack) and device_enum == DeviceEnum.REV2_EDITOR:
            return selected_track
        elif isinstance(current_track, ExternalSynthTrack):
            return current_track.audio_track

        return selected_track

    def _load_device_select_track(self, device_enum: DeviceEnum) -> None:
        track = self._get_instrument_track(device_enum)

        if device_enum.is_instrument:
            track.select()
            return

        device_to_select = self._get_device_to_select_for_insertion(track, device_enum)
        if device_to_select:
            track.device_insert_mode = Live.Track.DeviceInsertMode.selected_left
            self._device_component.select_device(track, device_to_select)
        else:
            track.device_insert_mode = Live.Track.DeviceInsertMode.selected_right
            if len(list(track.devices)) > 0:
                self._device_component.select_device(track, list(track.devices)[-1])

    def _on_device_loaded_event(self, _: DeviceLoadedEvent) -> None:
        """Select the default parameter if it exists"""
        device = Song.selected_track().devices.selected
        if device and device.enum and device.enum.default_parameter is not None:
            parameter = device.get_parameter_by_name(device.enum.default_parameter)
            self._device_component.selected_parameter = parameter

    def _on_dry_wet_device_added_event(self, _: DryWetDeviceAddedEvent) -> None:
        dry_wet_device = Song.selected_device()
        if not isinstance(dry_wet_device, RackDevice):
            return None

        devices = list(Song.selected_track().devices)
        try:
            next_device = devices[devices.index(dry_wet_device) + 1]
        except IndexError:
            return

        self._move_device(next_device._device, dry_wet_device.chains[1]._chain, 0)

    def _show_default_automation(self, clip: Clip) -> None:
        device = Song.selected_track().devices.selected
        assert device and device.enum.default_parameter, "Loaded device has no default parameter"
        parameter = device.get_parameter_by_name(device.enum.default_parameter)
        assert parameter is not None, "parameter not found"

        clip.automation.show_parameter_envelope(parameter)

    def _get_device_to_select_for_insertion(
        self, track: SimpleTrack, device_enum: DeviceEnum
    ) -> Optional[Device]:
        if len(list(track.devices)) == 0:
            return None

        # if we want to "reload" an existing device (hack for The God Particle)
        if device_enum.is_exclusive:
            previous_device = track.devices.get_one_from_enum(device_enum)
            if previous_device:
                return previous_device

        for device in track.devices:
            if not device.enum or device.is_instrument or device.is_midi:
                continue

            if device.enum.device_group_position > device_enum.device_group_position:
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
        master_handled = _switch_master_cpu_devices()

        if not master_handled:
            Backend.client().show_warning("Master devices not set up properly")
            return None

        _switch_black_box_devices()