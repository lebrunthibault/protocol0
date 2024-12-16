from dataclasses import dataclass, field
from typing import Optional, List, Union, Callable, Tuple, cast

from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.device_parameter.DeviceParamEnum import DeviceParamEnum
from protocol0.domain.lom.device_parameter.DeviceParameter import DeviceParameter
from protocol0.domain.lom.instrument.instrument.InstrumentParamEnum import (
    InstrumentParamEnum,
)
from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack


@dataclass(frozen=True)
class ParamDevice:
    device: Optional[Device]
    param: Union[DeviceParameter, Callable]


class ParamDeviceNotCallable(ParamDevice):
    param: DeviceParameter


@dataclass(frozen=True)
class DeviceParam:
    device_enum: DeviceEnum
    param_name: Union[DeviceParamEnum, str]
    auto_disable: bool = False
    automatable: bool = True
    scrollable: bool = True
    mutable: bool = False

    def get_param_device(self, track: SimpleTrack) -> Optional[ParamDevice]:
        device = track.devices.get_one_from_enum(self.device_enum)

        if not device:
            return None

        param = device.get_parameter_by_name(self.param_name)

        if not param:
            return None

        return ParamDevice(device, param)


@dataclass(frozen=True)
class TrackParam:
    callback: Callable[[SimpleTrack], DeviceParameter]
    automatable: bool = False
    limits: Optional[Tuple] = None

    def get_param_device(self, track: SimpleTrack) -> Optional[ParamDevice]:
        try:
            param = self.callback(track)
            return ParamDevice(None, param)
        except IndexError:
            pass

        return None


@dataclass(frozen=True)
class InstrumentParam:
    param_name: InstrumentParamEnum
    automatable: bool = True

    def get_param_device(self, track: SimpleTrack) -> Optional[ParamDevice]:
        instrument = track.instrument

        if not instrument or not instrument.device:
            return None
        param = None

        if track.instrument_rack_device:
            param = track.instrument_rack_device.get_parameter_by_name(self.param_name.name.lower())
            if param:
                return ParamDevice(track.instrument_rack_device, param)

        if self.param_name in instrument.PARAMETER_NAMES:
            param = instrument.device.get_parameter_by_name(
                instrument.PARAMETER_NAMES[self.param_name]
            )

        if param is None:
            return None

        return ParamDevice(instrument.device, param)


ParamConf = Union[DeviceParam, InstrumentParam, TrackParam]
ParamConfAndPD = Tuple[Optional[ParamConf], Optional[ParamDevice]]


@dataclass()
class XParam:
    name: str
    param_configs: List[ParamConf] = field(default_factory=lambda: [])
    value_items: Optional[List[int]] = None
    track: SimpleTrack = None  # type: ignore[assignment]

    def get_device_to_load(self, automatable: bool = False) -> Optional[DeviceEnum]:
        for param_conf in self.param_configs:
            if isinstance(param_conf, DeviceParam) and (not automatable or param_conf.automatable):
                return param_conf.device_enum

        return None

    def get_device_param(
        self, automatable: bool = False, mutable: bool = False
    ) -> Optional[ParamDeviceNotCallable]:
        for param_conf in self.param_configs:
            pd = param_conf.get_param_device(self.track)

            if (
                pd
                and not isinstance(param_conf, TrackParam)
                and isinstance(pd.param, DeviceParameter)
                and (not automatable or param_conf.automatable)
                and (not mutable or (isinstance(param_conf, DeviceParam) and param_conf.mutable))
            ):
                return cast(ParamDeviceNotCallable, pd)

        return None

    def get_scrollable(self, go_next: bool) -> ParamConfAndPD:
        track_params: Optional[ParamConfAndPD] = None

        for param_conf in self.param_configs:
            pd = param_conf.get_param_device(self.track)

            if pd and (not isinstance(param_conf, DeviceParam) or param_conf.scrollable):
                if isinstance(param_conf, TrackParam) and param_conf.limits:
                    param = param_conf.get_param_device(self.track).param
                    p_min, p_max = param_conf.limits
                    if (param.value <= p_min and not go_next) or (param.value >= p_max and go_next):
                        track_params = param_conf, pd
                        continue

                return param_conf, pd

        # in case there is no foldback parameter return the track param and go over limits
        if track_params:
            return track_params

        return None, None
