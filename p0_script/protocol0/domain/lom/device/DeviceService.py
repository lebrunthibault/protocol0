from functools import partial
from typing import Optional

import Live

from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.device.DeviceLoadedEvent import DeviceLoadedEvent
from protocol0.domain.lom.song.components.DeviceComponent import DeviceComponent
from protocol0.domain.lom.song.components.TrackComponent import get_track_by_name
from protocol0.domain.lom.song.components.TrackCrudComponent import TrackCrudComponent
from protocol0.domain.lom.track.group_track.TrackCategoryEnum import TrackCategoryEnum
from protocol0.domain.lom.track.group_track.ext_track.ExternalSynthTrack import ExternalSynthTrack
from protocol0.domain.lom.track.group_track.ext_track.SimpleMidiExtTrack import SimpleMidiExtTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.ApplicationView import ApplicationView
from protocol0.domain.shared.BrowserServiceInterface import BrowserServiceInterface
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.shared.Song import Song
from protocol0.shared.Undo import Undo
from protocol0.shared.sequence.Sequence import Sequence


class DeviceService(object):
    def __init__(
        self,
        track_crud_component: TrackCrudComponent,
        device_component: DeviceComponent,
        browser_service: BrowserServiceInterface,
    ) -> None:
        self._track_crud_component = track_crud_component
        self._device_component = device_component
        self._browser_service = browser_service
        DomainEventBus.subscribe(DeviceLoadedEvent, self._on_device_loaded_event)

    def load_device(self, enum_name: str, create_track: bool = False) -> Sequence:
        Undo.begin_undo_step()
        device_enum = DeviceEnum[enum_name]
        track = Song.selected_track()
        is_clip_view_visible = ApplicationView.is_clip_view_visible()

        self._load_device_select_track(device_enum, create_track)

        seq = Sequence()

        if device_enum.is_instrument:
            if create_track:
                seq.add(self._track_crud_component.create_midi_track)
                seq.add(lambda: setattr(Song.selected_track(), "name", device_enum.track_name))

                # if selected track is empty, delete it to make some room
                if len(track.clips) == 0 and not track.has_category(TrackCategoryEnum.BASS):
                    seq.add(track.delete)
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

        if device_enum.is_instrument:
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

    def _load_device_select_track(self, device_enum: DeviceEnum, create_track: bool) -> None:
        track = self._get_instrument_track(device_enum)

        if device_enum.is_instrument:
            if create_track:
                track_to_select_for_creation = self._get_track_to_select_for_creation(device_enum)
                if track_to_select_for_creation:
                    track_to_select_for_creation.select()
            else:
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

    def _get_track_to_select_for_creation(self, device_enum: DeviceEnum) -> Optional[SimpleTrack]:
        track = None
        if device_enum.is_harmony_instrument:
            track = get_track_by_name(TrackCategoryEnum.HARMONY.value, True)
        elif device_enum.is_melody_instrument:
            track = get_track_by_name(TrackCategoryEnum.MELODY.value, True)
        elif device_enum.is_bass_instrument:
            track = get_track_by_name(TrackCategoryEnum.BASS.value, True)

        if track:
            return track.sub_tracks[-1]

        return None

    def _on_device_loaded_event(self, _: DeviceLoadedEvent) -> None:
        """Select the default parameter if it exists"""
        device = Song.selected_track().devices.selected
        if device and device.enum and device.enum.default_parameter is not None:
            parameter = device.get_parameter_by_name(device.enum.default_parameter)
            self._device_component.selected_parameter = parameter

    def _show_default_automation(self, clip: Clip) -> None:
        device = Song.selected_track().devices.selected
        assert device.enum.default_parameter, "Loaded device has no default parameter"
        parameter = device.get_parameter_by_name(device.enum.default_parameter)
        assert parameter is not None, "parameter not found"

        clip.automation.show_parameter_envelope(parameter)

    def _get_device_to_select_for_insertion(
        self, track: SimpleTrack, device_enum: DeviceEnum
    ) -> Optional[Device]:
        if len(list(track.devices)) == 0:
            return None

        for device in track.devices:
            if not device.enum or device.is_instrument or device.is_midi:
                continue

            if device.enum.device_group_position > device_enum.device_group_position:
                return device

        return None
