from typing import Iterator, Union
from typing import TYPE_CHECKING, Optional, List, cast, Type

import Live

from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.utils.list import find_if
from protocol0.shared.types import T

if TYPE_CHECKING:
    from protocol0.shared.sequence.Sequence import Sequence
    from protocol0.domain.lom.song.components.ClipComponent import ClipComponent
    from protocol0.domain.lom.song.components.DeviceComponent import DeviceComponent
    from protocol0.domain.lom.song.components.PlaybackComponent import PlaybackComponent
    from protocol0.domain.lom.song.components.RecordingComponent import RecordingComponent
    from protocol0.domain.lom.song.components.SceneComponent import SceneComponent
    from protocol0.domain.lom.song.components.TempoComponent import TempoComponent
    from protocol0.domain.lom.song.components.QuantizationComponent import QuantizationComponent
    from protocol0.domain.lom.song.components.TrackComponent import TrackComponent
    from protocol0.domain.lom.scene.SceneService import SceneService
    from protocol0.domain.lom.track.TrackMapperService import TrackMapperService
    from protocol0.domain.track_recorder.RecordService import RecordService
    from protocol0.domain.lom.track.abstract_track.AbstractTrack import AbstractTrack
    from protocol0.domain.lom.track.group_track.AbstractGroupTrack import AbstractGroupTrack  # noqa
    from protocol0.domain.lom.track.group_track.ext_track.ExternalSynthTrack import (  # noqa
        ExternalSynthTrack,
    )
    from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
    from protocol0.domain.lom.track.group_track.DrumsTrack import DrumsTrack
    from protocol0.domain.lom.track.simple_track.audio.master.MasterTrack import MasterTrack
    from protocol0.domain.lom.track.group_track.VocalsTrack import VocalsTrack
    from protocol0.domain.lom.scene.Scene import Scene
    from protocol0.domain.lom.clip.Clip import Clip
    from protocol0.domain.lom.clip.MidiClip import MidiClip  # noqa
    from protocol0.domain.lom.clip_slot.ClipSlot import ClipSlot
    from protocol0.domain.lom.device.Device import Device
    from protocol0.domain.lom.device_parameter.DeviceParameter import DeviceParameter


class Song(object):
    """Read only facade for accessing song properties"""

    _INSTANCE: Optional["Song"] = None

    def __init__(
        self,
        live_song: Live.Song.Song,
        clip_component: "ClipComponent",
        device_component: "DeviceComponent",
        playback_component: "PlaybackComponent",
        quantization_component: "QuantizationComponent",
        recording_component: "RecordingComponent",
        scene_component: "SceneComponent",
        tempo_component: "TempoComponent",
        track_component: "TrackComponent",
        scene_service: "SceneService",
        track_mapper_service: "TrackMapperService",
        track_recorder_service: "RecordService",
    ) -> None:
        Song._INSTANCE = self

        self.__live_song = live_song

        self._clip_component = clip_component
        self._device_component = device_component
        self._playback_component = playback_component
        self._quantization_component = quantization_component
        self._recording_component = recording_component
        self._scene_component = scene_component
        self._tempo_component = tempo_component
        self._track_component = track_component

        self._track_mapper_service = track_mapper_service
        self._scene_service = scene_service
        self._track_recorder_service = track_recorder_service

    @classmethod
    def _live_song(cls) -> Live.Song.Song:
        return cls._INSTANCE.__live_song

    @classmethod
    def view(cls) -> Live.Song.Song.view:
        return cls._INSTANCE._live_song().view

    @classmethod
    def live_tracks(cls) -> Iterator[Live.Track.Track]:
        tracks = (
            list(cls._live_song().tracks) + cls.return_tracks() + [cls._live_song().master_track]
        )
        return (track for track in tracks)

    @classmethod
    def signature_numerator(cls) -> int:
        return cls._live_song().signature_numerator

    @classmethod
    def selected_track(cls, track_cls: Optional[Type[T]] = None) -> Union[T, "SimpleTrack"]:
        from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack

        track_cls = track_cls or SimpleTrack

        track = cls.live_track_to_simple_track(cls._live_song().view.selected_track)

        if not isinstance(track, track_cls):
            raise Protocol0Warning("track is not a %s" % track_cls.__name__)

        return track

    @classmethod
    def selected_or_soloed_track(cls) -> Union[T, "SimpleTrack"]:
        soloed_tracks = [t for t in Song.simple_tracks() if t.solo]
        track = Song.selected_track()

        if len(soloed_tracks) == 1:
            track = soloed_tracks[0]
            track.select()
        elif len(soloed_tracks) > 1:
            cls._INSTANCE._track_component.un_focus_all_tracks()
            track.solo = True

        if not track.is_foldable:
            track.arm_state.arm()

        return track

    @classmethod
    def current_track(cls) -> "AbstractTrack":
        return cls.selected_track().abstract_track

    @classmethod
    def current_external_synth_track(cls) -> "ExternalSynthTrack":
        from protocol0.domain.lom.track.group_track.ext_track.ExternalSynthTrack import (  # noqa
            ExternalSynthTrack,
        )

        if isinstance(Song.current_track(), ExternalSynthTrack):
            return cast(ExternalSynthTrack, Song.current_track())
        else:
            raise Protocol0Warning("current track is not an ExternalSynthTrack")

    @classmethod
    def abstract_tracks(cls) -> Iterator["AbstractTrack"]:
        return cls._INSTANCE._track_component.abstract_tracks

    @classmethod
    def live_track_to_simple_track(cls, live_track: Live.Track.Track) -> "SimpleTrack":
        """we use the live ptr instead of the track to be able to access outdated simple tracks on deletion"""
        track_mapping = cls._INSTANCE._track_mapper_service._live_track_id_to_simple_track
        if live_track._live_ptr not in track_mapping:
            existing_tracks = [str(track) for track in track_mapping.values()]
            raise Protocol0Error(
                "Couldn't find live track %s in _live_track_id_to_simple_track mapping : \n "
                "%s" % (live_track.name, "\n".join(existing_tracks))
            )

        return track_mapping[live_track._live_ptr]

    @classmethod
    def optional_simple_track_from_live_track(
        cls, live_track: Live.Track.Track
    ) -> Optional["SimpleTrack"]:
        try:
            return cls._INSTANCE._track_mapper_service._live_track_id_to_simple_track[
                live_track._live_ptr
            ]
        except KeyError:
            return None

    @classmethod
    def simple_tracks(
        cls, track_cls: Optional[Type[T]] = None
    ) -> Iterator[Union[T, "SimpleTrack"]]:
        from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack

        track_cls = track_cls or SimpleTrack

        tracks = (track for track in cls.all_simple_tracks() if track.IS_ACTIVE)

        return (track for track in tracks if isinstance(track, track_cls))

    @classmethod
    def all_simple_tracks(cls) -> Iterator["SimpleTrack"]:
        return (
            track
            for track in cls._INSTANCE._track_mapper_service._live_track_id_to_simple_track.values()
        )

    @classmethod
    def abstract_group_tracks(cls) -> Iterator["AbstractGroupTrack"]:
        from protocol0.domain.lom.track.group_track.AbstractGroupTrack import (  # noqa
            AbstractGroupTrack,
        )

        for track in cls.abstract_tracks():
            if isinstance(track, AbstractGroupTrack):
                yield track

    @classmethod
    def external_synth_tracks(cls) -> Iterator["ExternalSynthTrack"]:
        from protocol0.domain.lom.track.group_track.ext_track.ExternalSynthTrack import (  # noqa
            ExternalSynthTrack,
        )

        for track in cls.abstract_tracks():
            if isinstance(track, ExternalSynthTrack):
                yield track

    @classmethod
    def scrollable_tracks(cls) -> Iterator["AbstractTrack"]:
        return cls._INSTANCE._track_component.scrollable_tracks

    @classmethod
    def visible_tracks(cls) -> Iterator["AbstractTrack"]:
        return (t for t in cls.simple_tracks() if t.is_visible)

    @classmethod
    def armed_tracks(cls) -> Iterator["AbstractTrack"]:
        return (track for track in cls.abstract_tracks() if track.arm_state.is_armed)

    @classmethod
    def drums_track(cls) -> Optional["DrumsTrack"]:
        return cls._INSTANCE._track_mapper_service._drums_track

    @classmethod
    def vocals_track(cls) -> Optional["VocalsTrack"]:
        return cls._INSTANCE._track_mapper_service._vocals_track

    @classmethod
    def master_track(cls) -> Optional["MasterTrack"]:
        return cls._INSTANCE._track_mapper_service._master_track

    @classmethod
    def return_tracks(cls) -> List[Live.Track.Track]:
        return list(cls._live_song().return_tracks)

    @classmethod
    def scenes(cls) -> List["Scene"]:
        return cls._INSTANCE._scene_service.scenes

    @classmethod
    def active_scenes(cls) -> List["Scene"]:
        return cls._INSTANCE._scene_service.active_scenes

    @classmethod
    def last_scene(cls) -> "Scene":
        return cls._INSTANCE._scene_service.last_scene

    @classmethod
    def selected_scene(cls) -> "Scene":
        return cls._INSTANCE._scene_service.get_scene(cls._live_song().view.selected_scene)

    @classmethod
    def playing_scene(cls) -> Optional["Scene"]:
        from protocol0.domain.lom.scene.PlayingScene import PlayingScene

        return PlayingScene.get()

    @classmethod
    def looping_scene(cls) -> Optional["Scene"]:
        return cls._INSTANCE._scene_component.looping_scene_toggler.value

    @classmethod
    def last_manually_started_scene(cls) -> "Scene":
        from protocol0.domain.lom.scene.Scene import Scene

        return Scene.LAST_MANUALLY_STARTED_SCENE or cls.selected_scene()

    @classmethod
    def selected_clip_slot(
        cls, clip_slot_cls: Optional[Type[T]] = None
    ) -> Optional[Union[T, "ClipSlot"]]:
        from protocol0.domain.lom.clip_slot.ClipSlot import ClipSlot

        clip_slot_cls = clip_slot_cls or ClipSlot

        if cls.selected_track() is None:
            return None
        else:
            clip_slot = next(
                (
                    cs
                    for cs in cls.selected_track().clip_slots
                    if cs._clip_slot == cls._live_song().view.highlighted_clip_slot
                ),
                None,
            )

            if clip_slot is None:
                return None

            if not isinstance(clip_slot, clip_slot_cls):
                raise Protocol0Warning("clip slot is not a %s" % clip_slot_cls.__name__)

            return clip_slot

    @classmethod
    def selected_clip(
        cls, clip_cls: Optional[Type[T]] = None, raise_if_none: bool = True
    ) -> Optional[Union[T, "Clip"]]:
        from protocol0.domain.lom.clip.Clip import Clip

        clip_cls = clip_cls or Clip

        clip = cls.selected_clip_slot() and cls.selected_clip_slot().clip
        if clip is None:
            clip = cls.selected_track().clip_slots[Song.selected_scene().index].clip

        if clip is None and raise_if_none:
            raise Protocol0Warning("no selected clip")

        if clip is not None and not isinstance(clip, clip_cls):
            raise Protocol0Warning("clip is not a %s" % clip_cls.__name__)

        return clip

    @classmethod
    def selected_parameter(cls) -> Optional["DeviceParameter"]:
        return cls._INSTANCE._device_component.selected_parameter

    @classmethod
    def selected_device(cls) -> Optional["Device"]:
        return cls.selected_track().devices.selected

    @classmethod
    def is_playing(cls) -> bool:
        return cls._INSTANCE._playback_component.is_playing

    @classmethod
    def session_record(cls) -> bool:
        return cls._INSTANCE._recording_component.session_record

    @classmethod
    def is_track_recording(cls) -> bool:
        return cls._INSTANCE._track_recorder_service.is_recording

    @classmethod
    def midi_recording_quantization(cls) -> int:
        return cls._INSTANCE._quantization_component.midi_recording_quantization

    @classmethod
    def tempo(cls) -> float:
        return cls._INSTANCE._tempo_component.tempo

    @classmethod
    def current_beats_song_time(cls) -> Live.Song.BeatTime:
        # noinspection PyArgumentList
        return cls._live_song().get_current_beats_song_time()

    @classmethod
    def draw_mode(cls, draw_mode: bool) -> None:
        cls._INSTANCE._clip_component.draw_mode = draw_mode

    @classmethod
    def capture_midi(cls) -> None:
        cls._live_song().capture_midi()

    @classmethod
    def set_or_delete_cue(cls, time: float) -> Optional["Sequence"]:
        from protocol0.shared.sequence.Sequence import Sequence

        cue_points = cls._live_song().cue_points

        if find_if(lambda c: c.time == time, cue_points):
            return None

        cls._live_song().current_song_time = time

        return Sequence().defer().add(cls._live_song().set_or_delete_cue).done()
