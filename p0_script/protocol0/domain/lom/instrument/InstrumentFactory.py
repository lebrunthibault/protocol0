from typing import Optional, List, Type, TYPE_CHECKING

import protocol0.domain.lom.instrument.instrument as instrument_package
from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device.PluginDevice import PluginDevice
from protocol0.domain.lom.device.RackDevice import RackDevice
from protocol0.domain.lom.device.SimplerDevice import SimplerDevice
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface
from protocol0.domain.shared.utils.list import find_if
from protocol0.domain.shared.utils.utils import import_package
from protocol0.shared.logging.Logger import Logger

if TYPE_CHECKING:
    from protocol0.domain.lom.track.simple_track.SimpleTrack import SimpleTrack


class InstrumentFactory(object):
    _INSTRUMENT_CLASSES: List[Type[InstrumentInterface]] = []

    @classmethod
    def make_instrument(cls, track: "SimpleTrack") -> Optional[InstrumentInterface]:
        """
        If the instrument didn't change we keep the same instrument and don't instantiate a new one
        to keep instrument state
        """

        instrument_device = find_if(
            lambda d: d.is_instrument and not type(d) is RackDevice, track.devices.all
        )  # taking the 1st instrument found
        if instrument_device is None:
            return None

        instrument_class = cls._get_instrument_class(instrument_device)
        if instrument_class is None:
            return None

        if (
            instrument_class
            and isinstance(track.instrument, instrument_class)
            and track.instrument.device == instrument_device
        ):
            return track.instrument  # maintaining state
        else:
            rack_device = track.devices.get_device_or_rack_device(instrument_device)
            if rack_device:
                rack_device.register_observer(track)

            return instrument_class(instrument_device, rack_device)

    @classmethod
    def _get_instrument_class(cls, device: Device) -> Optional[Type[InstrumentInterface]]:
        if isinstance(device, PluginDevice):
            if not device.enum:
                Logger.warning(f"plugin device not detected : {device}")
                return None

            for _class in cls._get_instrument_classes():
                if _class.DEVICE == device.enum:
                    return _class
        elif isinstance(device, SimplerDevice):
            from protocol0.domain.lom.instrument.instrument.InstrumentSimpler import (
                InstrumentSimpler,
            )

            return InstrumentSimpler
        elif device._device.class_display_name == "Sampler":
            from protocol0.domain.lom.instrument.instrument.InstrumentSampler import (
                InstrumentSampler,
            )

            return InstrumentSampler

        return None

    @classmethod
    def _get_instrument_classes(cls) -> List[Type[InstrumentInterface]]:
        if not cls._INSTRUMENT_CLASSES:
            import_package(instrument_package)
            cls._INSTRUMENT_CLASSES = InstrumentInterface.__subclasses__()

        return cls._INSTRUMENT_CLASSES
