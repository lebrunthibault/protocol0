from functools import partial
from os.path import basename
from typing import List, cast, Any, Optional

import Live
from _Framework.CompoundElement import subject_slot_group
from _Framework.SubjectSlot import subject_slot

from protocol0.domain.lom.clip.AudioClip import AudioClip
from protocol0.domain.lom.clip_slot.AudioClipSlot import AudioClipSlot
from protocol0.domain.lom.track.TracksMappedEvent import TracksMappedEvent
from protocol0.domain.lom.track.group_track.DrumsTrack import DrumsTrack
from protocol0.domain.lom.track.simple_track.AudioToMidiClipMapping import AudioToMidiClipMapping
from protocol0.domain.lom.track.simple_track.CurrentMonitoringStateUpdatedEvent import (
    CurrentMonitoringStateUpdatedEvent,
)
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils.list import find_if
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence


def resize_clip_to_scene_length(
    track: "SimpleAudioTrack", clip_slot: Live.ClipSlot.ClipSlot
) -> None:
    clip = track.clip_slots[list(track._track.clip_slots).index(clip_slot)].clip

    if clip is None:
        return

    def set_clip_length() -> None:
        clip.loop.start = clip.loop.start_marker = 0
        clip.loop.end = clip.loop.end_marker = Song.scenes()[clip.index].length
        clip.show_loop()

    Scheduler.defer(set_clip_length)
    Scheduler.wait_ms(50, set_clip_length)  # hack to make the loop start on 1.1.1


class SimpleAudioTrack(SimpleTrack):
    CLIP_SLOT_CLASS = AudioClipSlot

    def __init__(self, *a: Any, **k: Any) -> None:
        super(SimpleAudioTrack, self).__init__(*a, **k)
        # don't flatten when the track did not change since last flatten (used to retry on error)
        self._needs_flattening = True

        self.clip_mapping = AudioToMidiClipMapping(self._data)
        self._data.restore()

        self._has_clip_listener.replace_subjects(self._track.clip_slots)
        self._current_monitoring_state_listener.subject = self._track

    @property
    def clip_slots(self) -> List[AudioClipSlot]:
        return cast(List[AudioClipSlot], super(SimpleAudioTrack, self).clip_slots)

    @property
    def clips(self) -> List[AudioClip]:
        return super(SimpleAudioTrack, self).clips  # noqa

    @subject_slot_group("has_clip")
    def _has_clip_listener(self, clip_slot: Live.ClipSlot.ClipSlot) -> None:
        self._needs_flattening = True

        clip = self.clip_slots[list(self._track.clip_slots).index(clip_slot)].clip
        if not clip:
            return None

        if any(isinstance(track, DrumsTrack) for track in self.group_tracks) and not clip.warping:

            def make_clip_loop() -> None:
                clip.warping = True
                clip.loop.start = -Song.scenes()[clip.index].length
                clip.loop.end = 0
                clip.looping = True
                clip.show_loop()

            Scheduler.defer(make_clip_loop)

    @subject_slot("current_monitoring_state")
    def _current_monitoring_state_listener(self) -> None:
        DomainEventBus.emit(CurrentMonitoringStateUpdatedEvent(self._track))

    def load_full_track(self) -> Sequence:
        assert isinstance(Song.current_track(), SimpleAudioTrack), "Track already loaded"
        matching_track = find_if(
            lambda t: t != self and t.name == self.name and not t.is_foldable,
            Song.simple_tracks(),
        )
        if matching_track is not None:
            matching_track.select()
            raise Protocol0Warning("Track already loaded")

        track_color = self.color
        seq = Sequence()
        seq.add(self.focus)
        seq.add(Backend.client().drag_matching_track)
        seq.wait_for_backend_event("track_focused")
        seq.add(partial(setattr, self, "color", track_color))
        seq.wait_for_backend_event("matching_track_loaded")
        seq.wait_for_event(TracksMappedEvent)
        seq.add(partial(Backend.client().close_explorer_window, "tracks"))
        seq.add(partial(Backend.client().show_success, "Track loaded"))
        return seq.done()

    def flatten(self, flatten_track: bool = True) -> Sequence:
        return super(SimpleAudioTrack, self).flatten(self._needs_flattening)

    def replace_clip_sample(
        self, dest_cs: AudioClipSlot, source_cs: AudioClipSlot = None, file_path: str = None
    ) -> Optional[Sequence]:
        assert source_cs is not None or file_path is not None, "provide clip_slot or file path"

        Logger.info(
            "Replacing clip: %s-> %s"
            % (basename(dest_cs.clip.file_path), basename(file_path or source_cs.clip.file_path))
        )

        device_params = self.devices.parameters
        automated_params = dest_cs.clip.automation.get_automated_parameters(device_params)

        # duplicate when no automation else manual action is needed
        if len(automated_params) == 0 and source_cs is not None:
            return dest_cs.replace_clip_sample(source_cs)
        else:
            if source_cs is not None:
                file_path = source_cs.clip.file_path

            return dest_cs.replace_clip_sample(None, file_path)

    def disconnect(self) -> None:
        self._data.save()

        super(SimpleAudioTrack, self).disconnect()
