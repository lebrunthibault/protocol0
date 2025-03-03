import Live

from protocol0.domain.lom.scene.Scene import Scene
from protocol0.domain.shared.ValueScroller import ValueScroller
from protocol0.shared.Song import Song


class SceneComponent(object):
    def __init__(self, song_view: Live.Song.Song.View) -> None:
        self._song_view = song_view

    def select_scene(self, scene: Scene) -> None:
        try:
            if scene._scene:
                self._song_view.selected_scene = scene._scene
        except RuntimeError:
            pass

    def scroll_scenes(self, go_next: bool) -> None:
        # have the scroller work the other way around
        go_next = not go_next
        next_scene = ValueScroller.scroll_values(
            Song.scenes(), Song.selected_scene(), go_next, rotate=False
        )
        self.select_scene(next_scene)
