from typing import List, Type, Optional, Iterator

import Live
from _Framework.CompoundElement import subject_slot_group
from _Framework.SubjectSlot import SlotManager

from protocol0.domain.lom.clip.Clip import Clip
from protocol0.domain.lom.clip_slot.ClipSlot import ClipSlot
from protocol0.domain.lom.clip_slot.ClipSlotHasClipEvent import ClipSlotHasClipEvent
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface
from protocol0.domain.lom.track.simple_track.SimpleTrackClips import SimpleTrackClips
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils.timing import defer
from protocol0.shared.Song import Song
from protocol0.shared.observer.Observable import Observable


class SimpleTrackClipSlots(SlotManager, Observable):
    # noinspection PyInitNewSignature
    def __init__(
        self,
        live_track: Live.Track.Track,
        clip_slot_class: Type[ClipSlot],
    ) -> None:
        super(SimpleTrackClipSlots, self).__init__()
        self._live_track = live_track
        self._clip_slot_class = clip_slot_class

        self._clip_slots: List[ClipSlot] = []

        self._clips = SimpleTrackClips(self)
        self._has_clip_listener.replace_subjects(live_track.clip_slots)

        self._instrument: Optional[InstrumentInterface] = None

    def __iter__(self) -> Iterator[ClipSlot]:
        return iter(self._clip_slots)

    def set_instrument(self, instrument: Optional[InstrumentInterface]) -> None:
        self._instrument = instrument

    @property
    def clip_slots(self) -> List[ClipSlot]:
        return self._clip_slots

    @property
    def clips(self) -> List[Clip]:
        return list(self._clips)

    @property
    def selected(self) -> ClipSlot:
        return list(self._clip_slots)[Song.selected_scene().index]

    def build(self) -> None:
        """create new ClipSlot objects and keep existing ones"""
        live_cs_to_cs = {cs._clip_slot: cs for cs in self.clip_slots}

        new_clip_slots: List[ClipSlot] = []
        for index, live_clip_slot in enumerate(list(self._live_track.clip_slots)):
            if live_clip_slot in live_cs_to_cs:
                clip_slot = live_cs_to_cs[live_clip_slot]
                # reindexing is necessary
                clip_slot.index = index
                if clip_slot.clip is not None:
                    clip_slot.clip.index = index
                new_clip_slots.append(clip_slot)
            else:
                clip_slot = self._clip_slot_class(live_clip_slot, index)
                clip_slot.register_observer(self)
                new_clip_slots.append(clip_slot)
        self._clip_slots[:] = new_clip_slots

        for cs in self._clip_slots:
            Scheduler.defer(cs.appearance.refresh)

        self._has_clip_listener.replace_subjects(self._live_track.clip_slots)

    def update(self, observable: Observable) -> None:
        if isinstance(observable, ClipSlot):
            self.notify_observers()

    @subject_slot_group("has_clip")
    @defer
    def _has_clip_listener(self, clip_slot: Live.ClipSlot.ClipSlot) -> None:
        DomainEventBus.emit(ClipSlotHasClipEvent(self._live_track))
        # noinspection PyBroadException
        try:
            if clip_slot.clip:
                clip_slot.clip.color_index = self._live_track.color_index
        except Exception:
            pass

    def disconnect(self) -> None:
        super(SimpleTrackClipSlots, self).disconnect()
        for clip_slot in self.clip_slots:
            clip_slot.disconnect()
