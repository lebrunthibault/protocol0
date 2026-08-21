"""Scene actions over the addressing grammar.

Scenes are targeted through a spec string (`scene` param, default SEL):
SEL | LAST | 1-based index | name | < / > relative to the selection.
"""
from typing import Optional

from protocol0.application.http.HttpServer import get_container
from protocol0.application.plugin.PluginInterface import PluginInterface
from protocol0.application.plugin.action import action
from protocol0.domain.lom.addressing.scene import resolve_scene
from protocol0.domain.lom.song.components.SceneComponent import SceneComponent
from protocol0.domain.lom.song.components.SceneCrudComponent import SceneCrudComponent
from protocol0.shared.sequence.Sequence import Sequence


class ScenePlugin(PluginInterface):
    name = "scene"

    @action
    def select(self, scene: str = "SEL") -> None:
        """Select a scene (scene: SEL, LAST, index, name, < / >)."""
        get_container().get(SceneComponent).select_scene(resolve_scene(scene))

    @action
    def fire(self, scene: str = "SEL") -> None:
        """Fire (launch) a scene."""
        resolve_scene(scene).fire()

    @action
    def scroll(self, direction: str = ">") -> None:
        """Scroll the scene selection (direction: > or <)."""
        # not SceneComponent.scroll_scenes: its direction is inverted on purpose
        # for the encoders; the grammar's < / > says what it means
        spec = "<" if direction.strip() == "<" else ">"
        get_container().get(SceneComponent).select_scene(resolve_scene(spec))

    @action
    def create(self, index: str = "") -> Sequence:
        """Create a scene (index: 1-based position, empty = at the end)."""
        position = int(index) - 1 if index.strip().isdigit() else None
        return get_container().get(SceneCrudComponent).create_scene(position)

    @action
    def duplicate(self, scene: str = "SEL") -> Sequence:
        """Duplicate a scene."""
        return get_container().get(SceneCrudComponent).duplicate_scene(resolve_scene(scene))

    @action
    def delete(self, scene: str = "SEL") -> Optional[Sequence]:
        """Delete a scene."""
        return get_container().get(SceneCrudComponent).delete_scene(resolve_scene(scene))

    @action
    def rename(self, name: str, scene: str = "SEL") -> None:
        """Rename a scene."""
        resolve_scene(scene).appearance.name = name
