from typing import TYPE_CHECKING

from protocol0.domain.lom.addressing.track import resolve_track
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.shared.Song import Song

if TYPE_CHECKING:
    from protocol0.domain.lom.clip.Clip import Clip


def resolve_clip(track_spec: str = "SEL", clip_spec: str = "SEL") -> "Clip":
    """Resolves a clip on a track (session view).

    track_spec: see resolve_track. clip_spec: SEL (the track's clip in the
    selected scene, default) | 1-based scene index ("3") | bare or quoted
    name (exact, then substring).
    """
    track = resolve_track(track_spec)
    spec = (clip_spec or "SEL").strip()

    if spec.upper() in ("SEL", ""):
        slot_index = Song.selected_scene().index
        slots = track.clip_slots
        if slot_index < len(slots) and slots[slot_index].clip is not None:
            return slots[slot_index].clip
        raise Protocol0Warning("no clip on '%s' in the selected scene" % track.name)

    if spec.isdigit():
        index = int(spec)
        slots = track.clip_slots
        if not 1 <= index <= len(slots):
            raise Protocol0Warning("no scene %s (%d scenes)" % (spec, len(slots)))
        clip = slots[index - 1].clip
        if clip is None:
            raise Protocol0Warning("no clip on '%s' in scene %s" % (track.name, spec))
        return clip

    name = spec[1:-1] if spec.startswith('"') and spec.endswith('"') and len(spec) > 1 else spec
    clips = track.clips
    exact = [c for c in clips if c.name and c.name.lower().strip() == name.lower().strip()]
    if exact:
        return exact[0]
    if not spec.startswith('"'):
        partial = [c for c in clips if c.name and name.lower().strip() in c.name.lower()]
        if partial:
            return partial[0]

    raise Protocol0Warning(
        "no clip matching '%s' on '%s' (clips: %s)"
        % (spec, track.name, ", ".join(c.name or "?" for c in clips))
    )
