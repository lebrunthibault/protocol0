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
from protocol0.shared.Song import Song


@dataclass(frozen=True)
class ParamDevice:
    device: Optional[Device]
    param: Union[DeviceParameter, Callable]


@dataclass(frozen=True)
class ParamDeviceNotCallable:
    device: Optional[Device]
    param: DeviceParameter


@dataclass(frozen=True)
class DeviceParam:
    device_enum: DeviceEnum
    param_name: Union[DeviceParamEnum, str]
    auto_disable: bool = False
    automatable: bool = True

    def get_param_device(self) -> Optional[ParamDevice]:
        device = Song.armed_or_selected_track().devices.get_one_from_enum(self.device_enum)

        if not device:
            return None

        param = device.get_parameter_by_name(self.param_name)

        if not param:
            return None

        return ParamDevice(device, param, self)


@dataclass(frozen=True)
class TrackParam:
    callback: Callable[[SimpleTrack], DeviceParameter]
    automatable: bool = False

    def get_param_device(self) -> ParamDevice:
        return ParamDevice(None, self.callback(Song.armed_or_selected_track()), self)


@dataclass(frozen=True)
class InstrumentParam:
    param_name: InstrumentParamEnum
    automatable: bool = True

    def get_param_device(self) -> Optional[ParamDevice]:
        instrument = Song.armed_or_selected_track().instrument

        if not instrument or not instrument.device:
            return None

        param = None
        if self.param_name in instrument.PARAMETER_NAMES:
            param = instrument.device.get_parameter_by_name(
                instrument.PARAMETER_NAMES[self.param_name]
            )
        elif callable(getattr(instrument, f"scroll_{self.param_name.name.lower()}", None)):
            param = getattr(instrument, f"scroll_{self.param_name.name.lower()}")

        if param is None:
            return None

        return ParamDevice(instrument.device, param, self)


ParamConf = Union[DeviceParam, InstrumentParam, TrackParam]


@dataclass(frozen=True)
class XParam:
    param_configs: List[ParamConf] = field(default_factory=lambda: [])
    value_items: Optional[List[int]] = None

    @property
    def name(self) -> str:
        return str(self.param_configs)

    def get_device_to_load(self) -> Optional[DeviceEnum]:
        for param_conf in self.param_configs:
            if isinstance(param_conf, DeviceParam):
                return param_conf.device_enum

        return None

    def get_device_param(self, automatable: bool = False) -> Optional[ParamDeviceNotCallable]:
        for param_conf in self.param_configs:
            pd = param_conf.get_param_device()
            if isinstance(pd.param, DeviceParameter) and (
                not automatable or param_conf.automatable
            ):
                return cast(ParamDeviceNotCallable, pd)

        return None

    def get_scrollable(self) -> Tuple[Optional[ParamConf], Optional[ParamDevice]]:
        for param_conf in self.param_configs:
            pd = param_conf.get_param_device()

            if pd:
                return param_conf, pd

        return None, None
