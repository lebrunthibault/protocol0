from dataclasses import dataclass, asdict, field
from functools import partial
from typing import Dict, Optional, List

from protocol0.application.ScriptDisconnectedEvent import ScriptDisconnectedEvent
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
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.infra.interface.session.SessionUpdatedEvent import SessionUpdatedEvent
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence


@dataclass
class AbletonSetPath:
    filename: Optional[str]


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
    track_count: int
    drum_rack_visible: bool


@dataclass
class AbletonSetModel:
    path_info: AbletonSetPath
    current_state: AbletonSetCurrentState


class AbletonSet(object):
    def __init__(self) -> None:
        self.path: Optional[str] = None
        self._title: Optional[str] = None
        self._model_cached: Optional[AbletonSetModel] = None

        DomainEventBus.subscribe(ScriptDisconnectedEvent, lambda _: self._disconnect())

        listened_events = [
            AbstractTrackNameUpdatedEvent,
            DrumRackLoadedEvent,
            SessionUpdatedEvent,
            TracksMappedEvent,
            ClipSlotPlayingStatusUpdatedEvent,
        ]

        for event in listened_events:
            DomainEventBus.subscribe(event, lambda _: self.notify())

        # fixes multiple notification on startup
        for event in (SelectedTrackChangedEvent,):
            Scheduler.wait(2, partial(DomainEventBus.subscribe, event, lambda _: self.notify()))

    def __repr__(self) -> str:
        return "AbletonSet(%s)" % self._title

    @property
    def is_unknown(self) -> bool:
        return self.path is None

    @property
    def is_test(self) -> bool:
        return self._title in ("Toto", "Default")

    def to_model(self) -> AbletonSetModel:
        return AbletonSetModel(
            path_info=AbletonSetPath(filename=self.path),
            current_state=AbletonSetCurrentState(
                selected_scene=Song.selected_scene().to_scene_state(),
                current_track=AbletonTrack(**Song.current_track().to_dict()),
                selected_track=AbletonTrack(**Song.selected_track().to_dict()),
                track_count=len(list(Song.simple_tracks())),
                drum_rack_visible=isinstance(Song.selected_track().instrument, InstrumentDrumRack),
            ),
        )

    def notify(self, force: bool = False) -> None:
        model = self.to_model()
        from protocol0.shared.logging.Logger import Logger

        Logger.dev(model.current_state.selected_scene.melody)

        if self._model_cached != model or force:
            seq = Sequence()
            seq.add(partial(Backend.client().post_set, asdict(model)))

            if self._title is None:
                seq.wait_for_backend_event("set_updated")
                seq.add(lambda: self._set_from_server_response(seq.res))  # type: ignore[arg-type]

            seq.done()

        self._model_cached = model

    def loop_notify_selected_scene(self) -> None:
        if (
            self._model_cached
            and self._model_cached.current_state.selected_scene
            != Song.selected_scene().to_scene_state()
        ):
            self.notify()

        Scheduler.wait_ms(1000, self.loop_notify_selected_scene)

    def _set_from_server_response(self, res: Dict) -> None:
        if self._title is not None:
            Logger.warning("Tried overwriting set title of %s" % self)
            # return

        self._title = res["path_info"]["name"]
        self.path = res["path_info"]["filename"]

    def _disconnect(self) -> None:
        Backend.client().close_set(self.path)
