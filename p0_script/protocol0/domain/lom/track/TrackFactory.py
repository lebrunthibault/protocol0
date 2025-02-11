from typing import Optional, Type

import Live

from protocol0.domain.lom.song.components.TrackCrudComponent import TrackCrudComponent
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.lom.track.simple_track.midi.SimpleMidiTrack import SimpleMidiTrack
from protocol0.domain.shared.BrowserServiceInterface import BrowserServiceInterface
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.shared.Song import Song


def _get_simple_track_class(track: Live.Track.Track) -> Type[SimpleTrack]:
    cls = None

    if track.has_midi_input:
        cls = SimpleMidiTrack
    elif track.has_audio_input:
        cls = SimpleAudioTrack

    if cls is None:
        raise Protocol0Error("Unknown track type")

    return cls


class TrackFactory(object):
    def __init__(
        self,
        track_crud_component: TrackCrudComponent,
        browser_service: BrowserServiceInterface,
    ) -> None:
        self._track_crud_component = track_crud_component
        self._browser_service = browser_service

    def create_simple_track(
        self, track: Live.Track.Track, index: int, cls: Optional[Type[SimpleTrack]] = None
    ) -> SimpleTrack:
        # checking first on existing tracks
        track_cls = cls or _get_simple_track_class(track)
        existing_simple_track = Song.optional_simple_track_from_live_track(track)

        if existing_simple_track and type(existing_simple_track) == track_cls:
            # reindexing tracks
            existing_simple_track._index = index
            return existing_simple_track

        return track_cls(track, index)
