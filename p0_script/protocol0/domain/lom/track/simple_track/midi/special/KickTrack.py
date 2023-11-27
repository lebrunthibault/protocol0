from typing import Any

from protocol0.domain.lom.device.MixerDevice import update_parent_compressor_from_volume
from protocol0.domain.lom.track.group_track.TrackCategoryEnum import TrackCategoryEnum
from protocol0.domain.lom.track.simple_track.midi.SimpleMidiTrack import SimpleMidiTrack
from protocol0.shared.Song import Song
from protocol0.shared.observer.Observable import Observable


class KickTrack(SimpleMidiTrack):
    TRACK_NAME = "Kick"

    def __init__(self, *a: Any, **k: Any) -> None:
        super(KickTrack, self).__init__(*a, **k)
        self.devices.mixer_device.volume.register_observer(self)

    def update(self, observable: Observable) -> None:
        if observable is self.devices.mixer_device.volume:
            update_parent_compressor_from_volume(self)
            Song.master_track().update_limiter_volume(self.volume)

    def has_category(self, category: TrackCategoryEnum) -> bool:
        return category == TrackCategoryEnum.DRUMS
