from typing import Optional, cast

import Live
from _Framework.SubjectSlot import SlotManager

from protocol0.domain.lom.scene.SceneAppearance import SceneAppearance
from protocol0.domain.lom.scene.SceneClips import SceneClips
from protocol0.domain.lom.scene.SceneFiredEvent import SceneFiredEvent
from protocol0.domain.lom.scene.SceneLength import SceneLength
from protocol0.domain.lom.scene.SceneName import SceneName
from protocol0.domain.lom.scene.ScenePlayingState import ScenePlayingState
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.utils.forward_to import ForwardTo
from protocol0.shared.Song import Song
from protocol0.shared.observer.Observable import Observable


class Scene(SlotManager):
    LAST_MANUALLY_STARTED_SCENE: Optional["Scene"] = None

    def __init__(self, live_scene: Live.Scene.Scene, index: int) -> None:
        super(Scene, self).__init__()
        self._scene = live_scene
        self.index = index
        self.live_id: int = self._scene._live_ptr

        self.clips = SceneClips(self.index)
        self._scene_length = SceneLength(self.clips, self.index)
        self.playing_state = ScenePlayingState(self.clips, self._scene_length)
        self.scene_name = SceneName(live_scene, self._scene_length, self.playing_state)
        self.appearance = SceneAppearance(live_scene, self.scene_name)

        # listeners
        self.clips.register_observer(self)
        # self.is_triggered_listener.subject = self._scene

    def __repr__(self) -> str:
        return "Scene(%s (%s))" % (self.name, self.index)

    def update(self, observable: Observable) -> None:
        if isinstance(observable, SceneClips):
            self.appearance.refresh()

    @property
    def next_scene(self) -> "Scene":
        if self.should_loop:
            return self
        else:
            next_scene = Song.scenes()[self.index + 1]
            if next_scene.skipped:
                return next_scene.next_scene
            else:
                return next_scene

    @property
    def should_loop(self) -> bool:
        return (
            self == Song.looping_scene()
            or self == Song.scenes()[-1]
            or Song.scenes()[self.index + 1].bar_length == 0
        )

    @property
    def previous_scene(self) -> "Scene":
        if self == Song.scenes()[0]:
            return self
        else:
            previous_scene = Song.scenes()[self.index - 1]
            if previous_scene.skipped:
                return previous_scene.previous_scene
            else:
                return previous_scene

    @property
    def is_triggered(self) -> bool:
        return bool(self._scene.is_triggered) if self._scene else False

    name = cast(str, ForwardTo("appearance", "name"))
    lower_name = cast(str, ForwardTo("appearance", "lower_name"))
    length = cast(float, ForwardTo("_scene_length", "length"))
    bar_length = cast(int, ForwardTo("_scene_length", "bar_length"))

    @property
    def skipped(self) -> bool:
        return self.lower_name.startswith("skip")

    def fire(self) -> None:
        # stop the previous scene in advance, using clip launch quantization
        DomainEventBus.emit(SceneFiredEvent(self.index))

        if self._scene:
            self._scene.fire()

    def disconnect(self) -> None:
        super(Scene, self).disconnect()
        self.scene_name.disconnect()
