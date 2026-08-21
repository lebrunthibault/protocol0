from typing import TYPE_CHECKING, List

from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.shared.Song import Song, find_track_or_none

if TYPE_CHECKING:
    from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack


def resolve_track(spec: str = "SEL") -> "SimpleTrack":
    """Resolves a track spec into a SimpleTrack.

    Specs: SEL (selected, default) | MST (master) | 1-based index ("2") |
    "name" (quoted: exact) | bare name (exact, then substring) | < / >
    (before / after the selected track, clamped).
    """
    spec = (spec or "SEL").strip()
    keyword = spec.upper()

    if keyword in ("SEL", ""):
        return Song.selected_track()
    if keyword == "MST":
        return Song.master_track()

    tracks: List["SimpleTrack"] = list(Song.simple_tracks())

    if keyword in ("<", ">"):
        selected = Song.selected_track()
        if selected not in tracks:
            raise Protocol0Warning("the selected track cannot be scrolled from")
        index = tracks.index(selected) + (1 if keyword == ">" else -1)
        return tracks[max(0, min(index, len(tracks) - 1))]

    if spec.isdigit():
        index = int(spec)
        if not 1 <= index <= len(tracks):
            raise Protocol0Warning("no track %s (%d tracks)" % (spec, len(tracks)))
        return tracks[index - 1]

    if spec.startswith('"') and spec.endswith('"') and len(spec) > 1:
        name = spec[1:-1]
        track = find_track_or_none(name, exact=True)
    else:
        track = find_track_or_none(spec, exact=True) or find_track_or_none(spec, exact=False)

    if track is None:
        raise Protocol0Warning(
            "no track matching '%s' (tracks: %s)" % (spec, ", ".join(t.name for t in tracks))
        )
    return track
