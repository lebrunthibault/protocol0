from functools import partial
from typing import Any, Optional

from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.device_parameter.DeviceParamEnum import DeviceParamEnum
from protocol0.domain.lom.track.CurrentMonitoringStateEnum import CurrentMonitoringStateEnum
from protocol0.domain.lom.track.routing.OutputRoutingTypeEnum import OutputRoutingTypeEnum
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.lom.track.simple_track.SimpleTrackSaveStartedEvent import (
    SimpleTrackSaveStartedEvent,
)
from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.scheduler.Scheduler import Scheduler
from protocol0.domain.shared.utils.utils import volume_to_db
from protocol0.shared.Song import Song


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

    @property
    def god_particle(self) -> Optional[Device]:
        return self.devices.get_one_from_enum(DeviceEnum.GOD_PARTICLE, all_devices=True)

    @property
    def adptr(self) -> Optional[Device]:
        return self.devices.get_one_from_enum(
            DeviceEnum.ADPTR_METRIC_AB, all_devices=True, enabled=True
        )

    def mute_for(self, duration: int) -> None:
        """
        Master track can not be muted so we set volume to 0
        duration: ms
        """
        self.volume = volume_to_db(0)
        Scheduler.wait_ms(duration, (partial(setattr, self, "volume", 0)))
        Scheduler.wait_ms(500, self._check_volume, unique=True)

    def balance_levels_to_zero(self) -> None:
        assert (
            self.devices and list(self.devices)[0].enum == DeviceEnum.UTILITY
        ), "Expected first device to be utility"

        utility: Device = list(self.devices)[0]
        gain = utility.get_parameter_by_name(DeviceParamEnum.GAIN).value
        from protocol0.shared.logging.Logger import Logger

        Logger.dev(f"master gain: {gain}")

        def is_template_bus_track(t: SimpleTrack) -> bool:
            return (
                t.output_routing.type == OutputRoutingTypeEnum.MASTER
                and t.current_monitoring_state == CurrentMonitoringStateEnum.IN
            )

        for track in Song.top_tracks():
            if (
                track.output_routing.type == OutputRoutingTypeEnum.MASTER
                and not is_template_bus_track(track)
            ):
                pass
            elif track.output_routing.track and is_template_bus_track(track.output_routing.track):
                pass
            else:
                break

            Logger.dev(f"-> {track}")

    def _check_volume(self) -> None:
        if self.volume != 0:
            Backend.client().show_warning("Master volume is not at 0 db, fixing")
            self.volume = 0
