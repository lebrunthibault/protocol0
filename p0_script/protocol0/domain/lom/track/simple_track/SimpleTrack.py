from functools import partial
from typing import cast, List, Optional, Dict, Iterable

import Live
from _Framework.SubjectSlot import SlotManager

from protocol0.domain.lom.clip.AudioClip import AudioClip
from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.lom.clip.MidiClip import MidiClip
from protocol0.domain.lom.clip_slot.ClipSlot import ClipSlot
from protocol0.domain.lom.device.RackDevice import RackDevice
from protocol0.domain.lom.device.SimpleTrackDevices import SimpleTrackDevices
from protocol0.domain.lom.device_parameter.DeviceParameter import DeviceParameter
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface
from protocol0.domain.lom.track.CurrentMonitoringStateEnum import CurrentMonitoringStateEnum
from protocol0.domain.lom.track.TracksMappedEvent import TracksMappedEvent
from protocol0.domain.lom.track.routing.OutputRoutingTypeEnum import OutputRoutingTypeEnum
from protocol0.domain.lom.track.routing.TrackInputRouting import TrackInputRouting
from protocol0.domain.lom.track.routing.TrackOutputRouting import TrackOutputRouting
from protocol0.domain.lom.track.simple_track.SimpleTrackAppearance import SimpleTrackAppearance
from protocol0.domain.lom.track.simple_track.SimpleTrackArmState import SimpleTrackArmState
from protocol0.domain.lom.track.simple_track.SimpleTrackClipSlots import SimpleTrackClipSlots
from protocol0.domain.lom.track.simple_track.SimpleTrackDeletedEvent import SimpleTrackDeletedEvent
from protocol0.domain.lom.track.simple_track.SimpleTrackSelectedEvent import (
    SimpleTrackSelectedEvent,
)
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils.forward_to import ForwardTo
from protocol0.domain.shared.utils.utils import volume_to_db, db_to_volume
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence


class SimpleTrack(SlotManager):
    # is_active is used to differentiate set tracks for return / master
    # we act only on active tracks
    IS_ACTIVE = True
    CLIP_SLOT_CLASS = ClipSlot

    # noinspection PyInitNewSignature
    def __init__(self, live_track: Live.Track.Track, index: int) -> None:
        super(SimpleTrack, self).__init__()
        self._track: Live.Track.Track = live_track
        self.index = index

        self.appearance = SimpleTrackAppearance(self._track)
        self.output_routing = TrackOutputRouting(self._track)

        self.live_id: int = live_track._live_ptr

        self.group_track: Optional[SimpleTrack] = None
        self.sub_tracks: List[SimpleTrack] = []

        self._instrument: Optional[InstrumentInterface] = None
        self._view = live_track.view

        self.devices = SimpleTrackDevices(live_track)

        self._clip_slots = SimpleTrackClipSlots(live_track, self.CLIP_SLOT_CLASS)
        self._clip_slots.build()

        # self.devices.register_observer(self)

        self.input_routing = TrackInputRouting(self._track)
        self._previous_output_routing_track: Optional[SimpleTrack] = None

        self.arm_state = SimpleTrackArmState(live_track)

        self.devices.build()

    def __repr__(self) -> str:
        return f"SimpleTrack({self.name})"

    device_insert_mode = cast(int, ForwardTo("_view", "device_insert_mode"))

    # def update(self, observable: Observable) -> None:
    #     if isinstance(observable, SimpleTrackDevices):
    #         # Refreshing is only really useful from simpler devices that change when a new sample is loaded
    #         if self.IS_ACTIVE and not self.is_foldable:
    #             self.instrument = InstrumentFactory.make_instrument(self)
    #
    #     return None

    name = cast(str, ForwardTo("appearance", "name"))
    lower_name = cast(str, ForwardTo("appearance", "lower_name"))

    @property
    def solo(self) -> bool:
        return self._track and self._track.solo

    @solo.setter
    def solo(self, solo: bool) -> None:
        if self._track:
            self._track.solo = solo

    @property
    def muted(self) -> bool:
        return self._track and self._track.mute

    @muted.setter
    def muted(self, mute: bool) -> None:
        if self._track:
            self._track.mute = mute

    @property
    def clip_slots(self) -> List[ClipSlot]:
        return list(self._clip_slots)

    @property
    def clips(self) -> List[Clip]:
        return [
            clip_slot.clip
            for clip_slot in self.clip_slots
            if clip_slot.has_clip and clip_slot.clip is not None
        ]

    @property
    def arrangement_clips(self) -> Iterable[Clip]:
        from protocol0.domain.lom.track.simple_track.midi.SimpleMidiTrack import SimpleMidiTrack

        clip_class = MidiClip if isinstance(self, SimpleMidiTrack) else AudioClip

        try:
            return (clip_class(clip, 0) for clip in self._track.arrangement_clips)
        except RuntimeError:
            return []

    @property
    def current_monitoring_state(self) -> CurrentMonitoringStateEnum:
        if self._track is None:
            return CurrentMonitoringStateEnum.AUTO

        try:
            return CurrentMonitoringStateEnum(self._track.current_monitoring_state)
        except RuntimeError:
            return CurrentMonitoringStateEnum.AUTO

    @current_monitoring_state.setter
    def current_monitoring_state(self, monitoring_state: CurrentMonitoringStateEnum) -> None:
        try:
            self._track.current_monitoring_state = monitoring_state.value  # noqa
        except Exception as e:
            Backend.client().show_warning(str(e))

    @property
    def instrument(self) -> Optional[InstrumentInterface]:
        return self._instrument

    @instrument.setter
    def instrument(self, instrument: Optional[InstrumentInterface]) -> None:
        self._instrument = instrument
        self.appearance.set_instrument(instrument)
        self._clip_slots.set_instrument(instrument)

    @property
    def instrument_rack_device(self) -> Optional[RackDevice]:
        if not self.instrument or not self.instrument.device:
            return None

        return self.devices.get_device_or_rack_device(self.instrument.device)

    @property
    def is_foldable(self) -> bool:
        return self._track and self._track.is_foldable

    @property
    def is_folded(self) -> bool:
        return bool(self._track.fold_state) if self.is_foldable and self._track else True

    @is_folded.setter
    def is_folded(self, is_folded: bool) -> None:
        if self._track and self.is_foldable:
            self._track.fold_state = int(is_folded)

    @property
    def is_collapsed(self) -> bool:
        return bool(self._track.view.is_collapsed)

    @is_collapsed.setter
    def is_collapsed(self, is_collapsed: bool) -> None:
        self._track.view.is_collapsed = is_collapsed

    @property
    def is_triggered(self) -> bool:
        return any(clip_slot.is_triggered for clip_slot in self.clip_slots)

    @property
    def volume(self) -> float:
        volume = self.devices.mixer_device.volume.value if self._track else 0
        return volume_to_db(volume)

    @volume.setter
    def volume(self, db_volume: float) -> None:
        assert db_volume <= 6, f"Got track volume overflow: {round(db_volume, 2)} db: {self}"

        volume = db_to_volume(db_volume)

        if self._track:
            DeviceParameter.set_live_device_parameter(self._track.mixer_device.volume, volume)

    @property
    def color(self) -> int:
        return self.appearance.color

    @color.setter
    def color(self, color_index: int) -> None:
        self.appearance.color = color_index

        for clip in self.clips:
            clip.color = color_index

    @property
    def is_playing(self) -> bool:
        return any(clip.is_playing for clip in self.clips)

    def toggle(self) -> None:
        self.muted = not self.muted

    def solo_toggle(self) -> None:
        self.solo = not self.solo

    def fire(self, scene_index: int) -> None:
        clip = self.clip_slots[scene_index].clip
        if clip is not None:
            clip.fire()

    def delete(self) -> Optional[Sequence]:
        if self.group_track and self.group_track.sub_tracks == [self]:
            Logger.warning(f"Cannot delete {self}: it is the only subtrack")
            return None
        DomainEventBus.emit(SimpleTrackDeletedEvent(self))
        return Sequence().wait_for_event(TracksMappedEvent).done()

    def delete_clip(self, clip: Clip) -> None:
        self._track.delete_clip(clip._clip)

    def scroll_volume(self, go_next: bool) -> None:
        """Editing directly the mixer device volume"""
        self.devices.mixer_device.volume.scroll(go_next)

    def duplicate_clip_to_arrangement(self, clip: Clip, time: float) -> None:
        self._track.duplicate_clip_to_arrangement(clip._clip, time)

    def clear_arrangement(self) -> None:
        try:
            for clip in self.arrangement_clips:
                self.delete_clip(clip)
        except RuntimeError:
            pass

    def remove_arrangement_muted_clips(self, start_time: float, end_time: float) -> None:
        try:
            for clip in self.arrangement_clips:
                if clip.start_marker >= start_time and clip.end_marker <= end_time and clip.muted:
                    self.delete_clip(clip)
        except RuntimeError:
            pass

    def toggle_ext_out_routing(self) -> None:
        if self.output_routing.type != OutputRoutingTypeEnum.EXT_OUT:
            self._previous_output_routing_track = self.output_routing.track
            self.output_routing.type = OutputRoutingTypeEnum.EXT_OUT
        else:
            if self._previous_output_routing_track:
                self.output_routing.track = self._previous_output_routing_track

    def un_collapse(self) -> None:
        # make it focused
        if not self.is_collapsed:
            self.is_collapsed = True

        self.is_collapsed = False

    def select(self) -> None:
        if self == Song.master_track():
            DomainEventBus.emit(SimpleTrackSelectedEvent(self._track))
            return None

        # hack to have the track fully shown
        last_track = list(Song.simple_tracks())[-1]
        if Song.selected_track().index < self.index and self != last_track:
            last_track.un_collapse()

        # hack : group tracks are not shown, only selected
        if self.is_foldable:
            self.sub_tracks[0].select()
            Backend.client().scroll(-35)
        else:
            self.un_collapse()

        DomainEventBus.emit(SimpleTrackSelectedEvent(self._track))

    @property
    def load_time(self) -> int:
        return self.devices.load_time

    def on_set_save(self) -> None:
        # there's no selected variation index listener
        if self.instrument_rack_device:
            self.instrument_rack_device.notify_observers()

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "color": self.color,
        }

    def disconnect(self) -> None:
        from protocol0.domain.lom.track.simple_track.SimpleTrackService import rename_tracks

        tracks = self.group_track.sub_tracks if self.group_track else Song.top_tracks()
        Scheduler.defer(partial(rename_tracks, tracks, self.name))

        self.appearance.disconnect()

        self.devices.disconnect()
        self._clip_slots.disconnect()
        if self.instrument:
            self.instrument.disconnect()
