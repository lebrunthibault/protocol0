from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface
from protocol0.domain.lom.instrument.preset.PresetDisplayOptionEnum import PresetDisplayOptionEnum
from protocol0.domain.lom.instrument.preset.preset_changer.ClipNotePresetChanger import (
    ClipNotePresetChanger,
)


class InstrumentDrumRack(InstrumentInterface):
    NAME = "Drum Rack"
    PRESET_DISPLAY_OPTION = PresetDisplayOptionEnum.NONE
    PRESET_CHANGER = ClipNotePresetChanger
