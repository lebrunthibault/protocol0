import Live
from _Framework.SubjectSlot import subject_slot, SlotManager
from typing import Optional

from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface
from protocol0.domain.lom.track.TrackColorEnum import TrackColorEnum
from protocol0.domain.lom.track.abstract_track.AbstractTrackNameUpdatedEvent import (
    AbstractTrackNameUpdatedEvent,
)
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.utils.string import title
from protocol0.domain.shared.utils.timing import defer
from protocol0.shared.observer.Observable import Observable


class AbstractTrackAppearance(SlotManager, Observable):
    def __init__(self, live_track: Live.Track.Track) -> None:
        super(AbstractTrackAppearance, self).__init__()
        self._live_track = live_track
        self._instrument: Optional[InstrumentInterface] = None
        self._name_listener.subject = live_track
        self._cached_name = self.name

    def set_instrument(self, instrument: Optional[InstrumentInterface]) -> None:
        self._instrument = instrument

    @subject_slot("name")
    @defer
    def _name_listener(self) -> None:
        self._cached_name = self.name

        if len(self.name) > 2:
            self.name = title(self.name)

    @property
    def name(self) -> str:
        return self._live_track.name if self._live_track else self._cached_name

    @name.setter
    def name(self, name: str) -> None:
        if self._live_track and name:
            self._live_track.name = str(name).strip()
            DomainEventBus.emit(AbstractTrackNameUpdatedEvent())

    @property
    def color(self) -> int:
        if self._live_track:
            return self._live_track.color_index
        else:
            return TrackColorEnum.DISABLED.value

    @color.setter
    def color(self, color_index: int) -> None:
        if self._live_track and color_index != self._live_track.color_index:
            self._live_track.color_index = color_index
