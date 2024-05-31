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
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
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

    def balance_levels_to_zero(self) -> None:
        assert (
            len(list(self.devices)) and list(self.devices)[0].enum == DeviceEnum.UTILITY
        ), "Expected first device to be utility"

        utility: Device = list(self.devices)[0]
        gain = utility.get_parameter_by_name(DeviceParamEnum.GAIN)
        assert gain.value >= 0, "Gain is negative"
        gain_db = gain.value * 35

        def is_template_bus_track(t: SimpleTrack) -> bool:
            return (
                t.output_routing.type == OutputRoutingTypeEnum.MASTER
                and t.current_monitoring_state == CurrentMonitoringStateEnum.IN
            )

        tracks = []

        for track in Song.top_tracks():
            if (
                track.output_routing.type == OutputRoutingTypeEnum.MASTER
                and not is_template_bus_track(track)
            ):
                tracks.append(track)
            elif (
                track.output_routing.track
                and track.output_routing.track != OutputRoutingTypeEnum.MASTER
                and is_template_bus_track(track.output_routing.track)
            ):
                tracks.append(track)

        for track in tracks:
            if track.volume + gain_db > 6:
                raise Protocol0Error(f"{track.name} is too hot")

        for track in tracks:
            track.volume += gain_db

        gain.value = 0
