from functools import partial
from typing import Callable

import Live

from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device.DeviceChain import DeviceChain
from protocol0.domain.lom.song.components.DeviceComponent import DeviceComponent
from protocol0.domain.lom.song.components.TrackCrudComponent import TrackCrudComponent
from protocol0.domain.lom.track.simple_track.midi.SimpleMidiTrack import SimpleMidiTrack
from protocol0.domain.shared.BrowserServiceInterface import BrowserServiceInterface
from protocol0.shared.Song import Song
from protocol0.shared.Undo import Undo
from protocol0.shared.sequence.Sequence import Sequence


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

    def load_device(self, name: str, create_track: bool = False) -> Sequence:
        Undo.begin_undo_step()

        track = Song.selected_track()

        if create_track and not isinstance(track, SimpleMidiTrack):
            seq = Sequence()
            seq.add(self._track_crud_component.create_midi_track)
            seq.defer()
            seq.add(partial(self._browser_service.load_device, name))
            seq.add(Undo.end_undo_step)
            return seq.done()

        track.device_insert_mode = Live.Track.DeviceInsertMode.selected_right
        if Song.selected_device() is None and len(list(track.devices)) > 0:
            self._device_component.select_device(track, list(track.devices)[-1])

        seq = Sequence()
        seq.defer()
        seq.add(partial(self._browser_service.load_device, name))
        seq.add(Undo.end_undo_step)
        return seq.done()

    def move_device(self, device: Device, chain: DeviceChain, position: int) -> Sequence:
        self._move_device(device._device, chain._chain, position)
        chain._devices_listener()  # workaround as chain devices listener doesn't seem to be called
        return Sequence().defer().done()
