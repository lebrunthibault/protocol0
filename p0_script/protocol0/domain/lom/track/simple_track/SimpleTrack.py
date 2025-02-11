from functools import partial
from typing import cast, List, Optional, Dict, Iterable

import Live
from _Framework.SubjectSlot import subject_slot

from protocol0.domain.lom.clip.AudioClip import AudioClip
from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.lom.clip.MidiClip import MidiClip
from protocol0.domain.lom.clip_slot.ClipSlot import ClipSlot
from protocol0.domain.lom.device.RackDevice import RackDevice
from protocol0.domain.lom.device.SimpleTrackDevices import SimpleTrackDevices
from protocol0.domain.lom.device_parameter.DeviceParameter import DeviceParameter
from protocol0.domain.lom.instrument.InstrumentFactory import InstrumentFactory
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface
from protocol0.domain.lom.track.CurrentMonitoringStateEnum import CurrentMonitoringStateEnum
from protocol0.domain.lom.track.TracksMappedEvent import TracksMappedEvent
from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
from protocol0.domain.lom.track.abstract_track.AbstractTrackSelectedEvent import (
    AbstractTrackSelectedEvent,
)
from protocol0.domain.lom.track.routing.OutputRoutingTypeEnum import OutputRoutingTypeEnum
from protocol0.domain.lom.track.routing.TrackInputRouting import TrackInputRouting
from protocol0.domain.lom.track.simple_track.SimpleTrackArmState import SimpleTrackArmState
from protocol0.domain.lom.track.simple_track.SimpleTrackClipSlots import SimpleTrackClipSlots
from protocol0.domain.lom.track.simple_track.SimpleTrackCreatedEvent import SimpleTrackCreatedEvent
from protocol0.domain.lom.track.simple_track.SimpleTrackDeletedEvent import SimpleTrackDeletedEvent
from protocol0.domain.lom.track.simple_track.SimpleTrackDisconnectedEvent import (
    SimpleTrackDisconnectedEvent,
)
from protocol0.domain.shared.ApplicationView import ApplicationView
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.ui.ColorEnum import ColorEnum
from protocol0.domain.shared.utils.forward_to import ForwardTo
from protocol0.domain.shared.utils.list import find_if
from protocol0.domain.shared.utils.utils import volume_to_db, db_to_volume
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.observer.Observable import Observable
from protocol0.shared.sequence.Sequence import Sequence


def route_track_to_bus(track: "SimpleTrack") -> None:
    if not track.has_audio_output:
        return None

    bus_suffix_dict = {
        "DR": ("Kick", "Snare", "Clap"),
        "Top": ("Hat", "Closed", "Open", "Perc", "Top"),
        "FX": ("Riser", "Down", "Trans", "Roll"),
        "Vox": ("Vox", "Vocal"),
        "PLK": ("PLK", "Pluck", "ARP"),
        "LD": ("LD", "Lead", "CHD", "Chord", "PD", "Pad"),
        "BS": ("BS", "Bass", "SUB"),
    }

    def get_bus_suffix() -> Optional[str]:
        for suffix, track_suffixes in bus_suffix_dict.items():
            for t_suffix in track_suffixes:
                if track.lower_name.startswith(t_suffix.lower()):
                    return suffix

        return None

    bus_track_group = list(Song.simple_tracks())[0]
    assert bus_track_group.is_foldable, "Could not find Bus group track"

    bus_suffix = get_bus_suffix()

    if not bus_suffix:
        Backend.client().show_warning(f"Couldn't find bus for {track}")
        track.muted = True
        return

    bus_track = find_if(
        lambda t: t.name.strip().upper().startswith(bus_suffix.upper()), bus_track_group.sub_tracks
    )

    if not bus_track:
        Backend.client().show_warning(f"Could not find `{bus_suffix}` bus track for {track.name}")
        track.muted = True
        return None

    track.output_routing.track = bus_track


class SimpleTrack(AbstractTrack):
    # is_active is used to differentiate set tracks for return / master
    # we act only on active tracks
    IS_ACTIVE = True
    CLIP_SLOT_CLASS = ClipSlot

    # noinspection PyInitNewSignature
    def __init__(self, live_track: Live.Track.Track, index: int) -> None:
        self._track: Live.Track.Track = live_track
        self._index = index

        super(SimpleTrack, self).__init__(self)

        self.live_id: int = live_track._live_ptr
        DomainEventBus.emit(SimpleTrackCreatedEvent(self))
        self.group_track: Optional[SimpleTrack] = self.group_track

        self.sub_tracks: List[SimpleTrack] = []

        self._instrument: Optional[InstrumentInterface] = None
        self._view = live_track.view

        self.devices = SimpleTrackDevices(live_track)

        self._clip_slots = SimpleTrackClipSlots(live_track, self.CLIP_SLOT_CLASS)
        self._clip_slots.build()
        self._clip_slots.register_observer(self)

        self.devices.register_observer(self)

        self.input_routing = TrackInputRouting(self._track)
        self._previous_output_routing_track: Optional[SimpleTrack] = None

        self.arm_state = SimpleTrackArmState(live_track)
        self.arm_state.register_observer(self)

        self._name_listener.subject = live_track

        self.devices.build()

    device_insert_mode = cast(int, ForwardTo("_view", "device_insert_mode"))

    def on_tracks_change(self) -> None:
        self._link_to_group_track()
        # because we traverse the tracks left to right : sub tracks will register themselves
        if self.is_foldable:
            self.sub_tracks[:] = []

    def _link_to_group_track(self) -> None:
        """Connect to the enclosing simple group track is any"""
        if self._track.group_track is None:
            self.group_track = None
            return None

        self.group_track = Song.live_track_to_simple_track(self._track.group_track)
        self.group_track.add_or_replace_sub_track(self)

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

    def update(self, observable: Observable) -> None:
        if isinstance(observable, SimpleTrackDevices):
            # Refreshing is only really useful from simpler devices that change when a new sample is loaded
            if self.IS_ACTIVE and not self.is_foldable:
                self.instrument = InstrumentFactory.make_instrument(self)

        return None

    @subject_slot("name")
    def _name_listener(self) -> None:
        from protocol0.domain.lom.track.simple_track.SimpleTrackService import rename_tracks

        tracks = self.group_track.sub_tracks if self.group_track else Song.top_tracks()
        Scheduler.defer(partial(rename_tracks, tracks))

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
    def output_meter_left(self) -> float:
        return self._track.output_meter_left if self._track else 0

    @property
    def has_midi_output(self) -> bool:
        return self._track.has_midi_output if self._track else False

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

    def stop(
        self,
        scene_index: Optional[int] = None,
        next_scene_index: Optional[int] = None,
        immediate: bool = False,
    ) -> None:
        if scene_index is None:
            self._track.stop_all_clips(not immediate)  # noqa
            return

        # let tail play
        try:
            clip = self.clip_slots[scene_index].clip
        except IndexError:
            return None

        if clip is not None and clip.is_playing:
            clip.stop(wait_until_end=True)

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
            DomainEventBus.emit(AbstractTrackSelectedEvent(self._track))
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

        DomainEventBus.emit(AbstractTrackSelectedEvent(self._track))

    def focus(self) -> Sequence:
        # track can disappear out of view if this is done later
        track_color = self.color

        self.color = ColorEnum.FOCUSED.value
        self.is_collapsed = True

        seq = Sequence()

        if not ApplicationView.is_browser_visible():
            ApplicationView.show_browser()
            seq.defer()

            # trick
            if Song.selected_track() == self.base_track:
                seq.add(next(Song.simple_tracks()).select)

        seq.add(self.select)
        seq.defer()

        # defensive : this will normally be done before
        seq.add(lambda: Scheduler.wait_ms(2000, partial(setattr, self, "color", track_color)))

        return seq.done()

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
        DomainEventBus.emit(SimpleTrackDisconnectedEvent(self))

        super(SimpleTrack, self).disconnect()
        self.devices.disconnect()
        self._clip_slots.disconnect()
        if self.instrument:
            self.instrument.disconnect()
