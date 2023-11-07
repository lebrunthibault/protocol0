from functools import partial

from typing import Any

from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.device_parameter.DeviceParamEnum import DeviceParamEnum
from protocol0.domain.lom.track.simple_track.SimpleTrackSaveStartedEvent import (
    SimpleTrackSaveStartedEvent,
)
from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils.utils import volume_to_db, clamp


class MasterTrack(SimpleAudioTrack):
    IS_ACTIVE = False

    def __init__(self, *a: Any, **k: Any) -> None:
        super(MasterTrack, self).__init__(*a, **k)

        self.devices.register_observer(self)
        DomainEventBus.subscribe(
            SimpleTrackSaveStartedEvent, self._on_simple_track_save_started_event
        )

    def _on_simple_track_save_started_event(self, _: SimpleTrackSaveStartedEvent) -> None:
        """youlean makes saving a track 10s + long"""
        youlean = self.devices.get_one_from_enum(DeviceEnum.YOULEAN)

        if youlean is not None:
            self.devices.delete(youlean)
            Backend.client().show_warning("Youlean removed")

    @property
    def muted(self) -> bool:
        return self.volume != 0

    def mute_for(self, duration: int) -> None:
        """
        Master track can not be muted so we set volume to 0
        duration: ms
        """
        self.volume = volume_to_db(0)
        Scheduler.wait_ms(duration, (partial(setattr, self, "volume", 0)))
        Scheduler.wait_ms(500, self._check_volume, unique=True)

    def _check_volume(self) -> None:
        if self.volume != 0:
            Backend.client().show_warning("Master volume is not at 0 db, fixing")
            self.volume = 0

    def update_limiter_volume(self, volume: float) -> None:
        l2 = self.devices.get_one_from_enum(DeviceEnum.L2_LIMITER)

        if not l2:
            return

        l2_threshold = l2.get_parameter_by_name(DeviceParamEnum.L2_THRESHOLD)

        l2_threshold.value = clamp((volume + 30 - 6) / 30, 0, 1)
