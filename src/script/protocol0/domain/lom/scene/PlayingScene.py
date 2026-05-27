from typing import Optional, List, TYPE_CHECKING

from protocol0.domain.lom.scene.PlayingSceneChangedEvent import PlayingSceneChangedEvent
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus

if TYPE_CHECKING:
    from protocol0.domain.lom.song.components.SceneComponent import SceneComponent
    from protocol0.domain.lom.scene.Scene import Scene


class PlayingScene(object):
    _INSTANCE: Optional["PlayingScene"] = None

    def __init__(self, scene_component: "SceneComponent") -> None:
        PlayingScene._INSTANCE = self

        self._scene_component = scene_component
        self._last_playing_scenes: List[Optional[Scene]] = [None] * 5

    @classmethod
    def get(cls) -> Optional["Scene"]:
        return cls._INSTANCE._last_playing_scenes[-1]

    @classmethod
    def set(cls, scene: Optional["Scene"]) -> None:
        if scene == cls.get():
            return None

        scenes = cls._INSTANCE._last_playing_scenes
        cls._INSTANCE._last_playing_scenes = scenes[1:] + [scene]

        # and select it
        if scene is not None:
            cls._INSTANCE._scene_component.select_scene(scene)

        DomainEventBus.emit(PlayingSceneChangedEvent())

        # deferring this until the previous playing scene has stopped
