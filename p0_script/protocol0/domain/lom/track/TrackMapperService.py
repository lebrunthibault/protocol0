import collections
from functools import partial
from typing import Optional, Dict, List

import Live
from _Framework.SubjectSlot import subject_slot, SlotManager

from protocol0.domain.lom.track.TrackFactory import TrackFactory
from protocol0.domain.lom.track.TracksMappedEvent import TracksMappedEvent
from protocol0.domain.lom.track.simple_track.CurrentMonitoringStateUpdatedEvent import (
    CurrentMonitoringStateUpdatedEvent,
)
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.lom.track.simple_track.SimpleTrackCreatedEvent import SimpleTrackCreatedEvent
from protocol0.domain.lom.track.simple_track.SimpleTrackService import rename_tracks
from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.lom.track.simple_track.audio.SimpleReturnTrack import SimpleReturnTrack
from protocol0.domain.lom.track.simple_track.audio.master.MasterTrack import MasterTrack
from protocol0.domain.lom.track.simple_track.audio.special.SimpleAutomationTrack import (
    SimpleAutomationTrack,
)
from protocol0.domain.lom.track.simple_track.midi.special.CthulhuTrack import CthulhuTrack
from protocol0.domain.shared.errors.error_handler import handle_errors
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.shared.Song import Song
from protocol0.shared.Undo import Undo
from protocol0.shared.sequence.Sequence import Sequence


class TrackMapperService(SlotManager):
    def __init__(self, live_song: Live.Song.Song, track_factory: TrackFactory) -> None:
        super(TrackMapperService, self).__init__()
        self._live_song = live_song
        self._track_factory = track_factory

        self._live_track_id_to_simple_track: Dict[int, SimpleTrack] = collections.OrderedDict()
        self._master_track: Optional[MasterTrack] = None

        self.tracks_listener.subject = self._live_song
        DomainEventBus.subscribe(SimpleTrackCreatedEvent, self._on_simple_track_created_event)
        DomainEventBus.subscribe(
            CurrentMonitoringStateUpdatedEvent, self._on_current_monitoring_state_updated_event
        )

    @subject_slot("tracks")
    @handle_errors()
    def tracks_listener(self) -> None:
        deleted_track_indexes = self._clean_tracks()

        previous_simple_track_count = len(list(Song.all_simple_tracks()))
        added_track_count = len(list(Song.live_tracks())) - previous_simple_track_count

        self._generate_simple_tracks()
        self._generate_abstract_group_tracks()

        for scene in Song.scenes():
            scene.on_tracks_change()

        seq = Sequence()
        if previous_simple_track_count and added_track_count > 0 and Song.selected_track():
            seq.add(partial(self._on_track_added, deleted_track_indexes))
            try:
                if added_track_count == 2:
                    tracks = (
                        list(Song.simple_tracks())[Song.selected_track().index - 1],
                        Song.selected_track(),
                    )
                    cthulhu_track: Optional[CthulhuTrack] = next(
                        filter(lambda t: isinstance(t, CthulhuTrack), tracks), None
                    )
                    if cthulhu_track:
                        # unselect both tracks
                        seq.add(list(Song.simple_tracks())[0].select)
                        seq.add(cthulhu_track.on_added)
            except IndexError:
                pass

        seq.add(partial(DomainEventBus.defer_emit, TracksMappedEvent()))
        seq.done()

    def _clean_tracks(self) -> List[int]:
        existing_track_ids = [track._live_ptr for track in list(Song.live_tracks())]
        deleted_ids = []
        deleted_indexes = []

        for track_id, simple_track in self._live_track_id_to_simple_track.items():
            if track_id not in existing_track_ids:
                simple_track.disconnect()
                deleted_ids.append(track_id)
                deleted_indexes.append(simple_track.index)

        for track_id in deleted_ids:
            del self._live_track_id_to_simple_track[track_id]

        return deleted_indexes

    def _generate_simple_tracks(self) -> None:
        """instantiate SimpleTracks (including return / master, that are marked as inactive)"""
        # instantiate set tracks
        for index, track in enumerate(list(self._live_song.tracks)):
            self._track_factory.create_simple_track(track, index)

        for index, track in enumerate(list(self._live_song.return_tracks)):
            self._track_factory.create_simple_track(track=track, index=index, cls=SimpleReturnTrack)

        self._master_track = self._track_factory.create_simple_track(
            self._live_song.master_track, 0, cls=MasterTrack
        )

        self._sort_simple_tracks()

        for track in Song.simple_tracks():
            track.on_tracks_change()

    def _on_track_added(self, deleted_track_indexes: List[int]) -> Optional[Sequence]:
        if not Song.selected_track().IS_ACTIVE:
            return None

        Undo.begin_undo_step()  # Live crashes on undo without this
        seq = Sequence()
        added_track = Song.current_track()
        seq.defer()

        tracks = (
            added_track.group_track.sub_tracks if added_track.group_track else Song.top_tracks()
        )
        seq.add(partial(rename_tracks, tracks, added_track.name))

        seq.add(added_track.on_added)
        if isinstance(added_track, SimpleTrack) and added_track.group_track:
            seq.add(added_track.group_track.abstract_group_track.on_added)

        seq.add(Song.current_track().arm_state.arm)

        seq.add(Undo.end_undo_step)
        return seq.done()

    def _on_current_monitoring_state_updated_event(
        self, event: CurrentMonitoringStateUpdatedEvent
    ) -> None:
        # handling replacement of a SimpleTrack by another
        track = Song.optional_simple_track_from_live_track(event.track)

        if isinstance(track, (SimpleAudioTrack, SimpleAutomationTrack)):
            self._track_factory.create_simple_track(track._track, track.index)

    def _on_simple_track_created_event(self, event: SimpleTrackCreatedEvent) -> None:
        """So as to be able to generate simple tracks with the abstract group track aggregate"""
        # handling replacement of a SimpleTrack by another
        previous_simple_track = Song.optional_simple_track_from_live_track(event.track._track)
        if previous_simple_track and previous_simple_track != event.track:
            self._replace_simple_track(previous_simple_track, event.track)

        self._live_track_id_to_simple_track[event.track.live_id] = event.track

    def _replace_simple_track(
        self, previous_simple_track: SimpleTrack, new_simple_track: SimpleTrack
    ) -> None:
        """disconnecting and removing from SimpleTrack group track and abstract_group_track"""
        new_simple_track._index = previous_simple_track._index
        previous_simple_track.disconnect()

        if (
            previous_simple_track.group_track is not None
            and previous_simple_track.group_track.abstract_group_track is not None
        ):
            previous_simple_track.group_track.abstract_group_track.add_or_replace_sub_track(
                new_simple_track, previous_simple_track
            )

        if previous_simple_track.abstract_group_track is not None:
            previous_simple_track.abstract_group_track.add_or_replace_sub_track(
                new_simple_track, previous_simple_track
            )

    def _sort_simple_tracks(self) -> None:
        sorted_dict = collections.OrderedDict()
        for track in Song.live_tracks():
            sorted_dict[track._live_ptr] = Song.live_track_to_simple_track(track)
        self._live_track_id_to_simple_track = sorted_dict

    def _generate_abstract_group_tracks(self) -> None:
        # 2nd pass : instantiate AbstractGroupTracks
        for track in Song.simple_tracks():
            if not track.is_foldable:
                continue

            previous_abstract_group_track = track.abstract_group_track
            abstract_group_track = self._track_factory.create_abstract_group_track(track)

            if (
                previous_abstract_group_track
                and previous_abstract_group_track != abstract_group_track
            ):
                previous_abstract_group_track.disconnect()

            abstract_group_track.on_tracks_change()
