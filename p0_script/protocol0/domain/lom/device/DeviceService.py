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
from protocol0.domain.lom.track.group_track.NormalGroupTrackEnum import NormalGroupTrackEnum
from protocol0.domain.lom.track.group_track.ext_track.ExternalSynthTrack import ExternalSynthTrack
from protocol0.domain.lom.track.group_track.ext_track.SimpleMidiExtTrack import SimpleMidiExtTrack
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.ApplicationView import ApplicationView
from protocol0.domain.shared.BrowserServiceInterface import BrowserServiceInterface
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.utils.list import find_if
from protocol0.shared.Song import Song
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
        device_enum = DeviceEnum[enum_name]
        track = self._track_to_select(device_enum)
        device_to_select = self._get_device_to_select_for_insertion(track, device_enum)

        if device_to_select:
            track.device_insert_mode = Live.Track.DeviceInsertMode.selected_left
            self._device_component.select_device(track, device_to_select)
        else:
            track.device_insert_mode = Live.Track.DeviceInsertMode.selected_right
            if len(list(track.devices)) > 0:
                self._device_component.select_device(track, list(track.devices)[-1])

        seq = Sequence()
        seq.add(track.select)
        if create_track and device_enum.is_instrument and track.instrument:
            if device_enum.is_bass_instrument:
                bass_track = get_track_by_name(NormalGroupTrackEnum.BASS.value, True)
                if bass_track:
                    seq.add(bass_track.sub_tracks[0].select)

            seq.add(self._track_crud_component.create_midi_track)
            seq.add(lambda: setattr(Song.selected_track(), "name", device_enum.value))

        seq.add(partial(self._browser_service.load_device_from_enum, device_enum))

        if (
            device_enum.default_parameter is not None
            and Song.selected_clip_slot() is not None
            and Song.selected_clip(raise_if_none=False) is not None
            and ApplicationView.is_clip_view_visible()
        ):
            seq.add(partial(self._create_default_automation, Song.selected_clip()))

        return seq.done()

    def _track_to_select(self, device_enum: DeviceEnum) -> SimpleTrack:
        selected_track = Song.selected_track()
        current_track = Song.current_track()

        # only case when we want to select the midi track of an ext track
        if isinstance(selected_track, SimpleMidiExtTrack) and device_enum == DeviceEnum.REV2_EDITOR:
            return selected_track
        elif isinstance(current_track, ExternalSynthTrack):
            return current_track.audio_track

        return selected_track

    def _on_device_loaded_event(self, _: DeviceLoadedEvent) -> None:
        """Select the default parameter if it exists"""
        device = Song.selected_track().devices.selected
        if device.enum.default_parameter is not None:
            parameter = device.get_parameter_by_name(device.enum.default_parameter)
            self._device_component.selected_parameter = parameter

    def _create_default_automation(self, clip: Clip) -> None:
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
            if device.is_instrument or not device.enum:
                continue

            if device.enum.device_group_position > device_enum.device_group_position:
                return device

        return None

    def scroll_high_pass_filter(self, go_next: bool) -> Sequence:
        eq_eight: Optional[Device] = find_if(
            lambda d: d.enum == DeviceEnum.EQ_EIGHT, Song.selected_track().devices
        )

        seq = Sequence()

        if not eq_eight:
            seq.add(partial(self.load_device, DeviceEnum.EQ_EIGHT.name))

        seq.add(partial(eq_eight.parameters[6].scroll, go_next))  # scroll frequency A
        return seq.done()

    def scroll_lfo_tool(self, go_next: bool) -> Sequence:
        lfo_tool: Optional[Device] = find_if(
            lambda d: d.enum == DeviceEnum.LFO_TOOL, Song.selected_track().devices
        )

        seq = Sequence()

        if not lfo_tool:
            seq.add(partial(self.load_device, DeviceEnum.LFO_TOOL.name))

        seq.add(partial(lfo_tool.parameters[1].scroll, go_next))  # scroll frequency A
        return seq.done()
