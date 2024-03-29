from typing import TYPE_CHECKING

from protocol0.domain.shared.LiveObject import liveobj_valid
from protocol0.infra.persistence.TrackDataEnum import TrackDataEnum
from protocol0.shared.logging.Logger import Logger

if TYPE_CHECKING:
    from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack


class TrackData(object):
    def __init__(self, track: "SimpleTrack") -> None:
        self._track = track

    def __repr__(self) -> str:
        return "TrackData(%s)" % self._track

    def save(self) -> None:
        if liveobj_valid(self._track._track):
            if self._track.instrument and self._track.instrument_rack_device:
                self._track._track.set_data(
                    TrackDataEnum.SELECTED_MACRO_VARIATION_INDEX.value,
                    self._track.instrument_rack_device.selected_variation_index,
                )

    def restore(self) -> None:
        # noinspection PyTypeChecker
        selected_variation_index: str = self._track._track.get_data(
            TrackDataEnum.SELECTED_MACRO_VARIATION_INDEX.value, None
        )

        if selected_variation_index is not None and int(selected_variation_index) >= 0:
            if not self._track.instrument_rack_device:
                return

            try:
                self._track.instrument_rack_device.selected_variation_index = int(
                    selected_variation_index
                )
            except RuntimeError as e:
                Logger.warning(e)
