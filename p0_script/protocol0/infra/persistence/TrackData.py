from typing import TYPE_CHECKING, Dict

from protocol0.domain.lom.track.simple_track.AudioToMidiClipMapping import AudioToMidiClipMapping
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
            from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import (
                SimpleAudioTrack,
            )

            if isinstance(self._track, SimpleAudioTrack) and self._track.clip_mapping:
                self._track._track.set_data(
                    TrackDataEnum.CLIP_MAPPING.value,
                    self._track.clip_mapping.to_dict(),
                )

            if self._track.instrument and self._track.instrument_rack_device:
                self._track._track.set_data(
                    TrackDataEnum.SELECTED_MACRO_VARIATION_INDEX.value,
                    self._track.instrument_rack_device.selected_variation_index,
                )

    def restore(self) -> None:
        # noinspection PyTypeChecker
        mapping_data: Dict = self._track._track.get_data(TrackDataEnum.CLIP_MAPPING.value, None)

        from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack

        if mapping_data is not None and isinstance(self._track, SimpleAudioTrack):
            self._track.clip_mapping = AudioToMidiClipMapping(self, mapping_data)

        selected_variation_index: str = self._track._track.get_data(
            TrackDataEnum.SELECTED_MACRO_VARIATION_INDEX.value, None
        )

        if selected_variation_index is not None and int(selected_variation_index) >= 0:
            assert (
                self._track.instrument_rack_device
            ), f"cannot find instrument rack device on {self._track}"
            try:
                self._track.instrument_rack_device.selected_variation_index = (
                    int(selected_variation_index)
                )
            except RuntimeError as e:
                Logger.warning(e)
