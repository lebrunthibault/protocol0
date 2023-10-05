from typing import Optional, List, Type

import protocol0.domain.lom.instrument.instrument as instrument_package
from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device.DrumRackDevice import DrumRackDevice
from protocol0.domain.lom.device.PluginDevice import PluginDevice
from protocol0.domain.lom.device.RackDevice import RackDevice
from protocol0.domain.lom.device.SimpleTrackDevices import SimpleTrackDevices
from protocol0.domain.lom.device.SimplerDevice import SimplerDevice
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface
from protocol0.domain.shared.utils.list import find_if
from protocol0.domain.shared.utils.utils import import_package


class InstrumentFactory(object):
    _INSTRUMENT_CLASSES: List[Type[InstrumentInterface]] = []

    @classmethod
    def make_instrument_from_simple_track(
        cls, devices: SimpleTrackDevices, instrument: Optional[InstrumentInterface], track_name: str
    ) -> Optional[InstrumentInterface]:
        """
        If the instrument didn't change we keep the same instrument and don't instantiate a new one
        to keep instrument state
        """

        instrument_device = find_if(
            lambda d: d.is_instrument and not type(d) is RackDevice, devices.all
        )  # taking the 1st instrument found
        if instrument_device is None:
            return None

        instrument_class = cls._get_instrument_class(instrument_device)
        if instrument_class is None:
            return None

        if (
            instrument_class
            and isinstance(instrument, instrument_class)
            and instrument.device == instrument_device
        ):
            return instrument  # maintaining state
        else:
            return instrument_class(instrument_device, track_name)

    @classmethod
    def _get_instrument_class(cls, device: Device) -> Optional[Type[InstrumentInterface]]:
        # checking for grouped devices
        if isinstance(device, DrumRackDevice):
            from protocol0.domain.lom.instrument.instrument.InstrumentDrumRack import (
                InstrumentDrumRack,
            )

            return InstrumentDrumRack
        elif isinstance(device, PluginDevice):
            assert device.enum, f"plugin device not detected : {device}"

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
