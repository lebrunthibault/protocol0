from functools import partial
from typing import Optional, Type

import Live

from protocol0.domain.lom.device.DrumRackService import DrumRackService
from protocol0.domain.lom.sample.SampleCategory import SampleCategory
from protocol0.domain.lom.sample.SampleCategoryEnum import SampleCategoryEnum
from protocol0.domain.lom.song.components.TrackCrudComponent import TrackCrudComponent
from protocol0.domain.lom.track.CurrentMonitoringStateEnum import CurrentMonitoringStateEnum
from protocol0.domain.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack
from protocol0.domain.lom.track.group_track.NormalGroupTrack import NormalGroupTrack
from protocol0.domain.lom.track.group_track.ext_track.ExternalSynthTrack import (
    ExternalSynthTrack,
)
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.lom.track.simple_track.audio.special.ResamplingTrack import ResamplingTrack
from protocol0.domain.lom.track.simple_track.audio.special.SimpleAutomationTrack import (
    SimpleAutomationTrack,
)
from protocol0.domain.lom.track.simple_track.midi.SimpleMidiTrack import SimpleMidiTrack
from protocol0.domain.lom.track.simple_track.midi.special.HatClosedTrack import HatClosedTrack
from protocol0.domain.lom.track.simple_track.midi.special.KickTrack import KickTrack
from protocol0.domain.lom.track.simple_track.midi.special.UsamoTrack import UsamoTrack
from protocol0.domain.shared.BrowserServiceInterface import BrowserServiceInterface
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.shared.Song import Song
from protocol0.shared.sequence.Sequence import Sequence


def _get_simple_track_class(track: Live.Track.Track) -> Type[SimpleTrack]:
    special_tracks = (UsamoTrack, KickTrack, HatClosedTrack, ResamplingTrack)

    cls = None

    if track.has_midi_input:
        cls = SimpleMidiTrack
    elif track.has_audio_input:
        cls = SimpleAudioTrack

    for special_track in special_tracks:
        if track.name.strip().lower() == special_track.TRACK_NAME.strip().lower():  # type: ignore[attr-defined]
            cls = special_track  # type: ignore

    try:
        if (
            track.has_audio_input
            and CurrentMonitoringStateEnum.from_value(track.current_monitoring_state)
            == CurrentMonitoringStateEnum.IN
        ):
            cls = SimpleAutomationTrack
    except RuntimeError:
        pass

    if cls is None:
        raise Protocol0Error("Unknown track type")

    return cls


class TrackFactory(object):
    def __init__(
        self,
        track_crud_component: TrackCrudComponent,
        browser_service: BrowserServiceInterface,
        drum_rack_service: DrumRackService,
    ) -> None:
        self._track_crud_component = track_crud_component
        self._browser_service = browser_service
        self._drum_rack_service = drum_rack_service

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

    def create_abstract_group_track(self, base_group_track: SimpleTrack) -> AbstractGroupTrack:
        previous_abstract_group_track = base_group_track.abstract_group_track

        if ExternalSynthTrack.is_group_track_valid(base_group_track):
            if isinstance(previous_abstract_group_track, ExternalSynthTrack):
                return previous_abstract_group_track
            else:
                return ExternalSynthTrack(base_group_track=base_group_track)

        # handling normal group track
        if isinstance(previous_abstract_group_track, NormalGroupTrack):
            return previous_abstract_group_track
        else:
            return NormalGroupTrack.make(base_group_track)

    def add_sample_track(self, category: SampleCategoryEnum, sample_sub_category: str) -> Sequence:
        sample_group_track = Song.drums_track()
        if sample_group_track is None:
            raise Protocol0Warning("Sample group track doesn't exist")

        if sample_sub_category.lower() not in category.subcategories:
            raise Protocol0Warning(
                "Cannot find %s sample category for '%s'" % (category, sample_sub_category)
            )

        sample_category = SampleCategory(category, sample_sub_category)

        sample_group_track.base_track.is_folded = False

        seq = Sequence()
        seq.add(
            partial(
                self._track_crud_component.create_midi_track, sample_category.create_track_index
            )
        )
        seq.add(lambda: setattr(Song.selected_track(), "volume", -15))
        seq.add(lambda: setattr(Song.selected_track(), "color", sample_category.color))

        # not creating clip here
        seq.add(partial(self._drum_rack_service.load_category_drum_rack, sample_category))

        return seq.done()
