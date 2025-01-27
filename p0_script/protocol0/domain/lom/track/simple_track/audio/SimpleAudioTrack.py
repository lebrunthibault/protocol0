from typing import List, cast, Any

import Live
from _Framework.CompoundElement import subject_slot_group
from _Framework.SubjectSlot import subject_slot

from protocol0.domain.lom.clip.AudioClip import AudioClip
from protocol0.domain.lom.clip_slot.AudioClipSlot import AudioClipSlot
from protocol0.domain.lom.track.simple_track.CurrentMonitoringStateUpdatedEvent import (
    CurrentMonitoringStateUpdatedEvent,
)
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.shared.Song import Song


def resize_clip_to_scene_length(
    track: "SimpleAudioTrack", clip_slot: Live.ClipSlot.ClipSlot
) -> None:
    clip = track.clip_slots[list(track._track.clip_slots).index(clip_slot)].clip

    if clip is None:
        return

    def set_clip_length() -> None:
        # noinspection PyBroadException
        try:
            clip.loop.start = clip.loop.start_marker = 0
            clip.loop.end = clip.loop.end_marker = Song.scenes()[clip.index].length
            clip.show_loop()
        except Exception:
            pass

    Scheduler.defer(set_clip_length)
    Scheduler.wait_ms(50, set_clip_length)  # hack to make the loop start on 1.1.1


class SimpleAudioTrack(SimpleTrack):
    CLIP_SLOT_CLASS = AudioClipSlot

    def __init__(self, *a: Any, **k: Any) -> None:
        super(SimpleAudioTrack, self).__init__(*a, **k)
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
        clip = self.clip_slots[list(self._track.clip_slots).index(clip_slot)].clip
        if not clip:
            return None

    @subject_slot("current_monitoring_state")
    def _current_monitoring_state_listener(self) -> None:
        DomainEventBus.emit(CurrentMonitoringStateUpdatedEvent(self._track))

    def disconnect(self) -> None:
        self._data.save()

        super(SimpleAudioTrack, self).disconnect()
