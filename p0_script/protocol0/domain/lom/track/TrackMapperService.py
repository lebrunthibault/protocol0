import collections
from typing import Optional, Dict, Type

import Live
from _Framework.SubjectSlot import subject_slot, SlotManager

from protocol0.domain.lom.track.TracksMappedEvent import TracksMappedEvent
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.lom.track.simple_track.SimpleTrackCreatedEvent import SimpleTrackCreatedEvent
from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.lom.track.simple_track.audio.SimpleReturnTrack import SimpleReturnTrack
from protocol0.domain.lom.track.simple_track.audio.master.MasterTrack import MasterTrack
from protocol0.domain.lom.track.simple_track.midi.SimpleMidiTrack import SimpleMidiTrack
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.errors.error_handler import handle_errors
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.shared.Song import Song


def get_simple_track_class(track: Live.Track.Track) -> Type[SimpleTrack]:
    if track.has_midi_input:
        return SimpleMidiTrack
    elif track.has_audio_input:
        return SimpleAudioTrack

    raise Protocol0Error("Unknown track type")


class TrackMapperService(SlotManager):
    def __init__(self, live_song: Live.Song.Song) -> None:
        super(TrackMapperService, self).__init__()
        self._live_song = live_song

        self._live_track_id_to_simple_track: Dict[int, SimpleTrack] = collections.OrderedDict()
        self._master_track: Optional[MasterTrack] = None

        self.tracks_listener.subject = self._live_song
        DomainEventBus.subscribe(SimpleTrackCreatedEvent, self._on_simple_track_created_event)

    @subject_slot("tracks")
    @handle_errors()
    def tracks_listener(self) -> None:
        self._clean_tracks()
        self._generate_simple_tracks()

        DomainEventBus.defer_emit(TracksMappedEvent())

    def _clean_tracks(self) -> None:
        existing_track_ids = [track._live_ptr for track in list(Song.live_tracks())]
        deleted_ids = []

        for track_id, simple_track in self._live_track_id_to_simple_track.items():
            if track_id not in existing_track_ids:
                simple_track.disconnect()
                deleted_ids.append(track_id)

        for track_id in deleted_ids:
            del self._live_track_id_to_simple_track[track_id]

    def _generate_simple_tracks(self) -> None:
        """instantiate SimpleTracks (including return / master, that are marked as inactive)"""
        # instantiate set tracks
        for index, track in enumerate(list(self._live_song.tracks)):
            self._create_simple_track(track, index)

        for index, track in enumerate(list(self._live_song.return_tracks)):
            self._create_simple_track(live_track=track, index=index, cls=SimpleReturnTrack)

        self._master_track = self._create_simple_track(
            self._live_song.master_track, 0, cls=MasterTrack
        )

        self._sort_simple_tracks()

        for track in Song.simple_tracks():
            if track._track.group_track:
                track.group_track = Song.live_track_to_simple_track(track._track.group_track)
                track.group_track.sub_tracks.append(track)

    def _create_simple_track(
        self, live_track: Live.Track.Track, index: int, cls: Optional[Type[SimpleTrack]] = None
    ) -> SimpleTrack:
        # checking first on existing tracks
        track_cls = cls or get_simple_track_class(live_track)
        existing_simple_track = Song.optional_simple_track_from_live_track(live_track)

        if existing_simple_track and type(existing_simple_track) == track_cls:
            # reindexing tracks
            existing_simple_track._index = index
            track = existing_simple_track
        else:
            track = track_cls(live_track, index)
        self._live_track_id_to_simple_track[track.live_id] = track

        return track

    def _on_simple_track_created_event(self, event: SimpleTrackCreatedEvent) -> None:
        # handling replacement of a SimpleTrack by another
        self._live_track_id_to_simple_track[event.track.live_id] = event.track

    def _sort_simple_tracks(self) -> None:
        sorted_dict = collections.OrderedDict()
        for track in Song.live_tracks():
            sorted_dict[track._live_ptr] = Song.live_track_to_simple_track(track)
        self._live_track_id_to_simple_track = sorted_dict
