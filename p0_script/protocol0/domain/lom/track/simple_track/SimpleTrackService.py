import re

from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.lom.track.simple_track.SimpleTrackFlattenedEvent import (
    SimpleTrackFlattenedEvent,
)
from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.utils.string import title
from protocol0.shared.Song import Song


def rename_tracks(group_track: SimpleTrack, track_name: str) -> None:
    """Rename track with duplicate names by numbering them"""

    def base_name(name: str, to_lower: bool = True) -> str:
        basename = re.sub(r"\s\d$", "", name.strip())
        if to_lower:
            return basename.lower()
        else:
            return basename

    duplicate_tracks = [
        t for t in group_track.sub_tracks if base_name(t.name) == base_name(track_name)
    ]

    if len(duplicate_tracks) > 1:
        for index, track in enumerate(duplicate_tracks):
            track.name = title(f"{base_name(track.name, to_lower=False)} {index + 1}")
    elif len(duplicate_tracks) == 1:
        duplicate_tracks[0].name = title(base_name(track_name, to_lower=False))


class SimpleTrackService(object):
    def __init__(self) -> None:
        DomainEventBus.subscribe(SimpleTrackFlattenedEvent, self._on_simple_track_flattened_event)

    def _on_simple_track_flattened_event(self, _: SimpleTrackFlattenedEvent) -> None:
        flattened_track = Song.selected_track(SimpleAudioTrack)

        for clip in flattened_track.clips:
            clip.looping = True
            clip.loop.start = 0
            clip.loop.end = clip.loop.end / 2

        flattened_track._needs_flattening = False
