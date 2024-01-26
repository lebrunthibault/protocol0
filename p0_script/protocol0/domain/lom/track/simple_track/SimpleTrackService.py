from collections import defaultdict
from typing import Optional, List

from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.lom.track.simple_track.SimpleTrackFlattenedEvent import (
    SimpleTrackFlattenedEvent,
)
from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.utils.string import title
from protocol0.domain.shared.utils.utils import track_base_name
from protocol0.shared.Song import Song


def rename_tracks(tracks: List[SimpleTrack], track_name: Optional[str] = None) -> None:
    """Rename track with duplicate names by numbering them"""

    tracks_by_base_name = defaultdict(list)

    for t in tracks:
        if track_name and track_base_name(t.name) != track_base_name(track_name):
            continue

        tracks_by_base_name[track_base_name(t.name)].append(t)

    for same_name_tracks in tracks_by_base_name.values():
        if len(same_name_tracks) > 1:
            for index, track in enumerate(same_name_tracks):
                name = track_base_name(track.name, to_lower=False)
                if index > 0:
                    name = f"{name} {index + 1}"
                track.name = name
        elif len(same_name_tracks) == 1:
            same_name_tracks[0].name = title(
                track_base_name(same_name_tracks[0].name, to_lower=False)
            )


class SimpleTrackService(object):
    def __init__(self) -> None:
        DomainEventBus.subscribe(SimpleTrackFlattenedEvent, self._on_simple_track_flattened_event)

    def _on_simple_track_flattened_event(self, _: SimpleTrackFlattenedEvent) -> None:
        flattened_track = Song.selected_track(SimpleAudioTrack)

        for clip in flattened_track.clips:
            clip.looping = True
            clip.loop.start = 0
            clip.loop.end = clip.loop.end / 2
            clip.loop.end_marker = clip.loop.end

        flattened_track._needs_flattening = False
