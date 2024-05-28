from dataclasses import dataclass, asdict, field
from functools import partial
from typing import Optional, List

from protocol0.domain.lom.track.SelectedTrackChangedEvent import SelectedTrackChangedEvent
from protocol0.domain.lom.track.TracksMappedEvent import TracksMappedEvent
from protocol0.domain.lom.track.abstract_track.AbstractTrackColorUpdatedEvent import (
    AbstractTrackColorUpdatedEvent,
)
from protocol0.domain.lom.track.abstract_track.AbstractTrackNameUpdatedEvent import (
    AbstractTrackNameUpdatedEvent,
)
from protocol0.domain.lom.track.group_track.TrackCategoryEnum import TrackCategoryEnum
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.lom.track.simple_track.SimpleTrackDeletedEvent import SimpleTrackDeletedEvent
from protocol0.domain.lom.track.simple_track.SimpleTrackDisconnectedEvent import (
    SimpleTrackDisconnectedEvent,
)
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils.timing import debounce
from protocol0.shared.Song import Song


@dataclass
class SceneTrackState:
    track_name: str
    group_name: str
    has_clip: bool
    is_playing: bool
    is_armed: bool

    @classmethod
    def create(
        cls, track: SimpleTrack, category: TrackCategoryEnum, scene_index: int
    ) -> "SceneTrackState":
        clip = track.clip_slots[scene_index].clip

        return cls(
            track_name=track.name,
            group_name=category.value,
            has_clip=clip is not None,
            is_playing=clip is not None and clip.is_playing,
            is_armed=track.arm_state.is_armed,
        )


@dataclass
class AbletonScene:
    drums: List[SceneTrackState] = field(default_factory=lambda: [])
    harmony: List[SceneTrackState] = field(default_factory=lambda: [])
    melody: List[SceneTrackState] = field(default_factory=lambda: [])
    bass: List[SceneTrackState] = field(default_factory=lambda: [])


@dataclass
class AbletonTrack:
    name: str
    color: str


@dataclass
class AbletonSetCurrentState:
    selected_track: AbletonTrack
    tracks: List[AbletonTrack]


class AbletonSet(object):
    def __init__(self) -> None:
        self._model_cached: Optional[AbletonSetCurrentState] = None

        listened_events = [
            AbstractTrackNameUpdatedEvent,
            TracksMappedEvent,
        ]

        for event in listened_events:
            DomainEventBus.subscribe(event, lambda _: self.notify())

        # fixes multiple notification on startup
        for event in (SelectedTrackChangedEvent,):
            Scheduler.wait(
                2, partial(DomainEventBus.subscribe, event, lambda _: self.notify(full=False))
            )

        DomainEventBus.subscribe(
            SimpleTrackDisconnectedEvent, self._on_simple_track_disconnected_event
        )
        DomainEventBus.subscribe(
            AbstractTrackNameUpdatedEvent, self._on_abstract_track_name_updated_event
        )
        DomainEventBus.subscribe(
            AbstractTrackColorUpdatedEvent, self._on_abstract_track_color_updated_event
        )

        Backend.client().clear_state()
        Scheduler.defer(self.notify)

    def __repr__(self) -> str:
        return "AbletonSet"

    def _on_simple_track_disconnected_event(self, event: SimpleTrackDeletedEvent) -> None:
        Backend.client().delete_track(event.track.name)

    def _on_abstract_track_name_updated_event(self, event: AbstractTrackNameUpdatedEvent) -> None:
        Backend.client().delete_track(event.previous_name)

    def _on_abstract_track_color_updated_event(self, event: AbstractTrackColorUpdatedEvent) -> None:
        Backend.client().update_track_color(
            {
                "track": asdict(AbletonTrack(**Song.selected_track().to_dict())),
                "previous_color": event.previous_color,
            }
        )

    def to_model(self, full: bool = True) -> AbletonSetCurrentState:
        tracks = []

        if full:
            tracks = [AbletonTrack(**track.to_dict()) for track in Song.simple_tracks()]

        return AbletonSetCurrentState(
            selected_track=AbletonTrack(**Song.selected_track().to_dict()),
            tracks=tracks,
        )

    @debounce(duration=20)
    def notify(self, full: bool = True, force: bool = False) -> None:
        model = self.to_model(full)

        if self._model_cached != model or force:
            from protocol0.shared.logging.Logger import Logger

            Logger.dev(asdict(model))
            Backend.client().post_current_state(asdict(model))

        self._model_cached = model
