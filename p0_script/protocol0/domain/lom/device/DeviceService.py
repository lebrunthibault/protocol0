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
from protocol0.domain.lom.track.simple_track.SimpleTrackService import rename_track
from protocol0.domain.shared.ApplicationView import ApplicationView
from protocol0.domain.shared.BrowserServiceInterface import BrowserServiceInterface
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.utils.concurrency import lock
from protocol0.domain.shared.utils.list import find_if
from protocol0.shared.Song import Song
from protocol0.shared.UndoFacade import UndoFacade
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
        UndoFacade.begin_undo_step()
        device_enum = DeviceEnum[enum_name]
        track = self._get_instrument_track(device_enum)
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

        if device_enum.is_instrument:
            if create_track:
                track_to_select_for_creation = self._get_track_to_select_for_creation(device_enum)
                if track_to_select_for_creation:
                    seq.add(track_to_select_for_creation.select)

                seq.add(self._track_crud_component.create_midi_track)
                seq.add(lambda: rename_track(Song.selected_track(), device_enum.track_name))
                # if selected track is empty, delete it to make some room
                if len(Song.selected_track().clips) == 0:
                    seq.add(Song.selected_track().delete)
            elif track.instrument:
                instrument_device = track.instrument_rack_device or track.instrument.device
                if instrument_device:
                    track.devices.delete(instrument_device)

        seq.add(partial(self._browser_service.load_device_from_enum, device_enum))

        if (
            device_enum.default_parameter is not None
            and Song.selected_clip_slot() is not None
            and Song.selected_clip(raise_if_none=False) is not None
            and ApplicationView.is_clip_view_visible()
        ):
            seq.add(partial(self._create_default_automation, Song.selected_clip()))

        seq.add(UndoFacade.end_undo_step)
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

    def _get_track_to_select_for_creation(self, device_enum: DeviceEnum) -> Optional[SimpleTrack]:
        track = None
        if device_enum.is_harmony_instrument:
            track = get_track_by_name(NormalGroupTrackEnum.HARMONY.value, True)
        elif device_enum.is_melody_instrument:
            track = get_track_by_name(NormalGroupTrackEnum.MELODY.value, True)
        elif device_enum.is_bass_instrument:
            track = get_track_by_name(NormalGroupTrackEnum.BASS.value, True)

        if track:
            return track.sub_tracks[-1]

        return None

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

    def scroll_volume(self, go_next: bool) -> None:
        rack_device = Song.selected_track().instrument_rack_device
        if rack_device:
            volume = rack_device.get_parameter_by_name("Volume")
            if volume:
                volume.scroll(go_next)
                return

        Song.selected_track().scroll_volume(go_next)

    @lock
    def scroll_low_pass_filter(self, go_next: bool) -> Optional[Sequence]:
        rack_device = Song.selected_track().instrument_rack_device
        if rack_device:
            filter_param = rack_device.get_parameter_by_name("Filter")
            if filter_param:
                filter_param.scroll(go_next)
                return None

        eq_eight = Song.selected_track().devices.get_one_from_enum(DeviceEnum.EQ_EIGHT)

        seq = Sequence()

        if not eq_eight:
            seq.add(partial(self.load_device, DeviceEnum.EQ_EIGHT.name))
        else:
            eq_eight.is_enabled = True
            frequency = eq_eight.get_parameter_by_name("8 Frequency A")
            frequency.scroll(go_next)

        return seq.done()

    def toggle_eq(self) -> None:
        eq_eight = Song.selected_track().devices.get_one_from_enum(DeviceEnum.EQ_EIGHT)
        if eq_eight:
            eq_eight.is_enabled = not eq_eight.is_enabled

    @lock
    def scroll_high_pass_filter(self, go_next: bool) -> Sequence:
        eq_eight = Song.selected_track().devices.get_one_from_enum(DeviceEnum.EQ_EIGHT)

        seq = Sequence()

        if not eq_eight:
            seq.add(partial(self.load_device, DeviceEnum.EQ_EIGHT.name))
        else:
            eq_eight.is_enabled = True
            frequency = eq_eight.get_parameter_by_name("1 Frequency A")
            frequency.scroll(go_next)

        return seq.done()

    def scroll_release(self, go_next: bool) -> None:
        rack_device = Song.selected_track().instrument_rack_device
        if rack_device:
            release = rack_device.get_parameter_by_name("Release")
            if release:
                release.scroll(go_next)

    def scroll_reverb(self, go_next: bool) -> None:
        rack_device = Song.selected_track().instrument_rack_device
        if rack_device:
            reverb = rack_device.get_parameter_by_name("Reverb")
            if reverb:
                reverb.scroll(go_next)
                return

        insert_reverb = Song.selected_track().devices.get_one_from_enum(DeviceEnum.INSERT_REVERB)
        if insert_reverb:
            from protocol0.shared.logging.Logger import Logger

            Logger.dev(insert_reverb.parameters[1])
            insert_reverb.parameters[1].scroll(go_next)
        else:
            sends = Song.selected_track().devices.mixer_device.sends
            if len(sends):
                sends[-1].scroll(go_next)

    def scroll_delay(self, go_next: bool) -> None:
        rack_device = Song.selected_track().instrument_rack_device
        if rack_device:
            delay = rack_device.get_parameter_by_name("Delay")
            if delay:
                delay.scroll(go_next)
                return

        insert_delay = Song.selected_track().devices.get_one_from_enum(DeviceEnum.INSERT_DELAY)
        if insert_delay:
            from protocol0.shared.logging.Logger import Logger

            Logger.dev(insert_delay.parameters[1])
            insert_delay.parameters[1].scroll(go_next)

    @lock
    def scroll_lfo_tool(self, go_next: bool) -> Sequence:
        lfo_tool: Optional[Device] = find_if(
            lambda d: d.enum == DeviceEnum.LFO_TOOL, Song.selected_track().devices
        )

        seq = Sequence()

        if not lfo_tool:
            seq.add(partial(self.load_device, DeviceEnum.LFO_TOOL.name))
        else:
            seq.add(partial(lfo_tool.parameters[1].scroll, go_next))

        return seq.done()
