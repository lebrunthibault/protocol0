from functools import partial
from typing import Optional, Type, Dict

from _Framework.SubjectSlot import SlotManager

from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.device.PluginDevice import PluginDevice
from protocol0.domain.lom.device.RackDevice import RackDevice
from protocol0.domain.lom.instrument.instrument.InstrumentParamEnum import InstrumentParamEnum
from protocol0.domain.lom.instrument.preset.InstrumentPreset import InstrumentPreset
from protocol0.domain.lom.instrument.preset.InstrumentPresetList import InstrumentPresetList
from protocol0.domain.lom.instrument.preset.PresetDisplayOptionEnum import PresetDisplayOptionEnum
from protocol0.domain.lom.instrument.preset.preset_changer.PresetChangerInterface import (
    PresetChangerInterface,
)
from protocol0.domain.lom.instrument.preset.preset_changer.ProgramChangePresetChanger import (
    ProgramChangePresetChanger,
)
from protocol0.domain.lom.instrument.preset.preset_importer.PresetImporterFactory import (
    PresetImporterFactory,
)
from protocol0.domain.lom.instrument.preset.preset_initializer.PresetInitializerDevicePresetName import (
    PresetInitializerDevicePresetName,
)
from protocol0.domain.lom.instrument.preset.preset_initializer.PresetInitializerInterface import (
    PresetInitializerInterface,
)
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
    PRESETS_PATH = ""
    PRESET_EXTENSION = ""
    PRESET_DISPLAY_OPTION = PresetDisplayOptionEnum.NAME
    PRESET_CHANGER: Type[PresetChangerInterface] = ProgramChangePresetChanger
    PRESET_INITIALIZER: Type[PresetInitializerInterface] = PresetInitializerDevicePresetName
    INSTRUMENT_TRACK_NAME = ""
    PARAMETER_NAMES: Dict[InstrumentParamEnum, str] = {}

    # noinspection PyInitNewSignature
    def __init__(self, device: Optional[Device], rack_device: Optional[RackDevice] = None) -> None:
        super(InstrumentInterface, self).__init__()
        self.device = device

        preset_importer = PresetImporterFactory.create_importer(
            device, self.PRESETS_PATH, self.PRESET_EXTENSION
        )
        preset_initializer = self.PRESET_INITIALIZER(device)
        preset_changer = self.PRESET_CHANGER(device)

        self.preset_list = InstrumentPresetList(
            preset_importer, preset_initializer, preset_changer, device, rack_device
        )

    def __repr__(self) -> str:
        return self.__class__.__name__

    @property
    def name(self) -> str:
        if self.PRESET_DISPLAY_OPTION == PresetDisplayOptionEnum.NAME and self.selected_preset:
            return self.selected_preset.name
        elif (
            self.PRESET_DISPLAY_OPTION == PresetDisplayOptionEnum.CATEGORY
            and self.preset_list.selected_category
        ):
            return self.preset_list.selected_category
        elif self.NAME:
            return self.NAME
        else:
            return self.device.name

    @property
    def full_name(self) -> str:
        full_name = self.device.name

        if self.selected_preset:
            full_name += f": {self.selected_preset.name}"
        elif (
            isinstance(self.device, PluginDevice)
            and self.device.selected_preset
            and self.device.selected_preset != "Default"
        ):
            full_name += f": {self.device.selected_preset}"

        return full_name

    def on_loaded(self, device_enum: DeviceEnum) -> None:
        return

    @property
    def selected_preset(self) -> Optional[InstrumentPreset]:
        return self.preset_list.selected_preset
