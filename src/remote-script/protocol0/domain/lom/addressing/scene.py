from typing import TYPE_CHECKING

from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.shared.Song import Song

if TYPE_CHECKING:
    from protocol0.domain.lom.scene.Scene import Scene


def resolve_scene(spec: str = "SEL") -> "Scene":
    """Resolves a scene spec into a Scene.

    Specs: SEL (selected, default) | LAST | 1-based index ("3") | "name"
    (quoted: exact) | bare name (exact, then substring) | < / > (before /
    after the selected scene, clamped).
    """
    spec = (spec or "SEL").strip()
    keyword = spec.upper()
    scenes = Song.scenes()

    if keyword in ("SEL", ""):
        return Song.selected_scene()
    if keyword == "LAST":
        return scenes[-1]

    if keyword in ("<", ">"):
        index = Song.selected_scene().index + (1 if keyword == ">" else -1)
        return scenes[max(0, min(index, len(scenes) - 1))]

    if spec.isdigit():
        index = int(spec)
        if not 1 <= index <= len(scenes):
            raise Protocol0Warning("no scene %s (%d scenes)" % (spec, len(scenes)))
        return scenes[index - 1]

    name = spec[1:-1] if spec.startswith('"') and spec.endswith('"') and len(spec) > 1 else spec
    exact = [s for s in scenes if s.name and s.name.lower().strip() == name.lower().strip()]
    if exact:
        return exact[0]
    if not spec.startswith('"'):
        partial = [s for s in scenes if s.name and name.lower().strip() in s.name.lower()]
        if partial:
            return partial[0]

    raise Protocol0Warning(
        "no scene matching '%s' (scenes: %s)" % (spec, ", ".join(s.name or "?" for s in scenes))
    )
