from typing import Optional

from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.device_parameter.DeviceParamEnum import DeviceParamEnum
from protocol0.domain.lom.set.MixingService import balance_bus_levels_to_zero, SimpleTrackToDevices
from protocol0.domain.lom.track.CurrentMonitoringStateEnum import CurrentMonitoringStateEnum
from protocol0.domain.lom.track.routing.OutputRoutingTypeEnum import OutputRoutingTypeEnum
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack
from protocol0.domain.lom.track.simple_track.audio.SimpleAudioTrack import SimpleAudioTrack
from protocol0.domain.shared.errors.Protocol0Error import Protocol0Error
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.shared.Song import Song


class MasterTrack(SimpleAudioTrack):
    IS_ACTIVE = False

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

    def activate_adptr_filter(self, filter_type: str) -> None:
        if not self.adptr:
            raise Protocol0Warning("ADPTR not found")

        filter_switch = self.adptr.get_parameter_by_name(DeviceParamEnum.FILTER_SWITCH)

        if not filter_switch:
            raise Protocol0Warning("Filter Switch not mapped on ADPTR")

        filter_preset = self.adptr.get_parameter_by_name(DeviceParamEnum.FILTER_PRESET)
        if not filter_preset:
            raise Protocol0Warning("Filter Preset not mapped on ADPTR")

        filter_preset_to_value = {
            "sub": 0.6,
            "bass": 0.8,
            "low_mid": 0,
            "mid": 0.2,
            "high": 0.4,
        }

        filter_preset.value = filter_preset_to_value[filter_type]

    def balance_levels_to_zero(self) -> SimpleTrackToDevices:
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

        bus_compressors: SimpleTrackToDevices = {}

        for track in tracks:
            track.volume += gain_db
            if track.is_foldable:
                bus_compressors = {**bus_compressors, **balance_bus_levels_to_zero(track)}

        gain.value = 0

        return bus_compressors
