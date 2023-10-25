from dataclasses import dataclass, asdict, field
from functools import partial
from typing import Optional, List

from protocol0.domain.lom.clip_slot.ClipSlotPlayingStatusUpdatedEvent import (
    ClipSlotPlayingStatusUpdatedEvent,
)
from protocol0.domain.lom.device.DrumRackLoadedEvent import DrumRackLoadedEvent
from protocol0.domain.lom.instrument.instrument.InstrumentDrumRack import InstrumentDrumRack
from protocol0.domain.lom.track.SelectedTrackChangedEvent import SelectedTrackChangedEvent
from protocol0.domain.lom.track.TracksMappedEvent import TracksMappedEvent
from protocol0.domain.lom.track.abstract_track.AbstractTrackNameUpdatedEvent import (
    AbstractTrackNameUpdatedEvent,
)
from protocol0.domain.lom.track.simple_track.SimpleTrackArmedEvent import SimpleTrackArmedEvent
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils.timing import debounce
from protocol0.infra.interface.session.SessionUpdatedEvent import SessionUpdatedEvent
from protocol0.shared.Song import Song


@dataclass
class SceneTrackState:
    track_name: str
    group_name: str
    has_clip: bool
    is_playing: bool
    is_armed: bool


@dataclass
class AbletonScene:
    drums: List[SceneTrackState] = field(default_factory=lambda: [])
    harmony: List[SceneTrackState] = field(default_factory=lambda: [])
    melody: List[SceneTrackState] = field(default_factory=lambda: [])
    bass: List[SceneTrackState] = field(default_factory=lambda: [])


@dataclass
class AbletonTrack:
    name: str
    type: str
    index: int


@dataclass
class AbletonSetCurrentState:
    selected_scene: AbletonScene
    current_track: AbletonTrack
    selected_track: AbletonTrack
    drum_rack_visible: bool


class AbletonSet(object):
    def __init__(self) -> None:
        self._model_cached: Optional[AbletonSetCurrentState] = None

        listened_events = [
            AbstractTrackNameUpdatedEvent,
            DrumRackLoadedEvent,
            SessionUpdatedEvent,
            TracksMappedEvent,
            ClipSlotPlayingStatusUpdatedEvent,
            SimpleTrackArmedEvent,
        ]

        for event in listened_events:
            DomainEventBus.subscribe(event, lambda _: self.notify())

        # fixes multiple notification on startup
        for event in (SelectedTrackChangedEvent,):
            Scheduler.wait(2, partial(DomainEventBus.subscribe, event, lambda _: self.notify()))

    def __repr__(self) -> str:
        return "AbletonSet"

    def to_model(self) -> AbletonSetCurrentState:
        return AbletonSetCurrentState(
            selected_scene=Song.selected_scene().to_scene_state(),
            current_track=AbletonTrack(**Song.current_track().to_dict()),
            selected_track=AbletonTrack(**Song.selected_track().to_dict()),
            drum_rack_visible=isinstance(Song.selected_track().instrument, InstrumentDrumRack),
        )

    @debounce(duration=20)
    def notify(self, force: bool = False) -> None:
        model = self.to_model()

        if self._model_cached != model or force:
            Backend.client().post_current_state(asdict(model))

        self._model_cached = model

    def loop_notify_selected_scene(self) -> None:
        if (
            self._model_cached
            and self._model_cached.selected_scene != Song.selected_scene().to_scene_state()
        ):
            self.notify()

        Scheduler.wait_ms(1000, self.loop_notify_selected_scene)
