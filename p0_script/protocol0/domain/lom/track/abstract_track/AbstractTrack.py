from typing import Optional, List, cast, TYPE_CHECKING

import Live
from _Framework.SubjectSlot import SlotManager

from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface
from protocol0.domain.lom.track.TrackDisconnectedEvent import TrackDisconnectedEvent
from protocol0.domain.lom.track.abstract_track.AbstrackTrackArmState import AbstractTrackArmState
from protocol0.domain.lom.track.abstract_track.AbstractTrackAppearance import (
    AbstractTrackAppearance,
)
from protocol0.domain.lom.track.routing.TrackOutputRouting import TrackOutputRouting
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.utils.forward_to import ForwardTo

if TYPE_CHECKING:
    from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack


class AbstractTrack(SlotManager):
    def __init__(self, track: "SimpleTrack") -> None:
        super(AbstractTrack, self).__init__()
        # TRACKS
        self._track: Live.Track.Track = track._track
        self.base_track: SimpleTrack = track
        self.group_track: Optional[AbstractTrack] = None
        self.sub_tracks: List[AbstractTrack] = []

        # MISC
        self.arm_state: AbstractTrackArmState = AbstractTrackArmState(self._track)
        self.appearance = AbstractTrackAppearance(self._track)
        self.output_routing = TrackOutputRouting(self._track)

    def __repr__(self) -> str:
        return "%s : %s (%s)" % (self.__class__.__name__, self._track.name, self.index + 1)

    @property
    def index(self) -> int:
        return self.base_track._index

    def add_or_replace_sub_track(
        self, sub_track: "AbstractTrack", previous_sub_track: Optional["AbstractTrack"] = None
    ) -> None:
        if sub_track in self.sub_tracks:
            return

        if sub_track._track == self._track:  # same track
            return

        if previous_sub_track is None or previous_sub_track not in self.sub_tracks:
            self.sub_tracks.append(sub_track)
        else:
            sub_track_index = self.sub_tracks.index(previous_sub_track)
            self.sub_tracks[sub_track_index] = sub_track

    @property
    def instrument(self) -> Optional[InstrumentInterface]:
        return None

    name = cast(str, ForwardTo("appearance", "name"))
    lower_name = cast(str, ForwardTo("appearance", "lower_name"))

    @property
    def color(self) -> int:
        raise NotImplementedError

    @color.setter
    def color(self, color_index: int) -> None:
        raise NotImplementedError

    @property
    def solo(self) -> bool:
        return self._track and self._track.solo

    @solo.setter
    def solo(self, solo: bool) -> None:
        if self._track:
            self._track.solo = solo

    @property
    def is_visible(self) -> bool:
        return self._track and self._track.is_visible

    @property
    def muted(self) -> bool:
        return self._track and self._track.mute

    @muted.setter
    def muted(self, mute: bool) -> None:
        if self._track:
            self._track.mute = mute

    @property
    def has_audio_output(self) -> bool:
        return self._track.has_audio_output if self._track else False

    def select(self) -> None:
        self.base_track.select()

    def fire(self, scene_index: int) -> None:
        raise NotImplementedError

    def stop(
        self,
        scene_index: Optional[int] = None,
        next_scene_index: Optional[int] = None,
        immediate: bool = False,
    ) -> None:
        raise NotImplementedError

    def disconnect(self) -> None:
        super(AbstractTrack, self).disconnect()
        self.appearance.disconnect()
        DomainEventBus.emit(TrackDisconnectedEvent(self))
