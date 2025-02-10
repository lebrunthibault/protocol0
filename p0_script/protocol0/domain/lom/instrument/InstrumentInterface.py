from functools import partial
from typing import Optional, Type, Dict

from _Framework.SubjectSlot import SlotManager

from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.device.PluginDevice import PluginDevice
from protocol0.domain.lom.device.RackDevice import RackDevice
from protocol0.domain.lom.instrument.instrument.InstrumentParamEnum import InstrumentParamEnum
from protocol0.domain.lom.track.TracksMappedEvent import TracksMappedEvent
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.shared.Song import Song
from protocol0.shared.sequence.Sequence import Sequence


def load_instrument_track(instrument_cls: Type["InstrumentInterface"]) -> Sequence:
    insert_track = Song.current_track().base_track
    track_color = insert_track.color

    seq = Sequence()
    seq.add(insert_track.focus)
    seq.add(partial(Backend.client().load_instrument_track, instrument_cls.INSTRUMENT_TRACK_NAME))
    seq.wait_for_backend_event("instrument_loaded")
    seq.add(partial(setattr, insert_track, "color", track_color))
    seq.defer()
    seq.wait_for_event(TracksMappedEvent)
    seq.add(partial(Backend.client().close_explorer_window, "default"))
    return seq.done()


class InstrumentInterface(SlotManager):
    NAME = ""
    DEVICE: Optional[DeviceEnum] = None
    INSTRUMENT_TRACK_NAME = ""
    PARAMETER_NAMES: Dict[InstrumentParamEnum, str] = {}

    # noinspection PyInitNewSignature
    def __init__(self, device: Optional[Device], rack_device: Optional[RackDevice] = None) -> None:
        super(InstrumentInterface, self).__init__()
        self.device = device

    def __repr__(self) -> str:
        return self.__class__.__name__

    @property
    def name(self) -> str:
        if self.NAME:
            return self.NAME
        else:
            return self.device.name

    @property
    def full_name(self) -> str:
        full_name = self.device.name

        if (
            isinstance(self.device, PluginDevice)
            and self.device.selected_preset
            and self.device.selected_preset != "Default"
        ):
            full_name += f": {self.device.selected_preset}"

        return full_name

    def on_loaded(self, device_enum: DeviceEnum) -> None:
        return
