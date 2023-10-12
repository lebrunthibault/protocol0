from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.lom.track.simple_track.SimpleTrackFlattenedEvent import (
    SimpleTrackFlattenedEvent,
)
from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.shared.Song import Song


def rename_track(track: SimpleTrack, name: str) -> None:
    track_names = [track.name.lower().strip() for track in Song.simple_tracks()]

    if name.lower().strip() not in track_names:
        track.name = name
        return

    count = 2
    new_name = name
    while new_name.lower().strip() in track_names:
        new_name = f"{name} {count}"
        count += 1

    track.name = new_name


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
