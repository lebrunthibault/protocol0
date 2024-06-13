from protocol0.domain.lom.instrument.InstrumentColorEnum import InstrumentColorEnum
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface
from protocol0.domain.lom.instrument.preset.PresetDisplayOptionEnum import PresetDisplayOptionEnum
from protocol0.domain.lom.instrument.preset.preset_changer.ClipNotePresetChanger import (
    ClipNotePresetChanger,
)


class InstrumentDrumRack(InstrumentInterface):
    NAME = "Drum Rack"
    TRACK_COLOR = InstrumentColorEnum.SIMPLER
    PRESET_DISPLAY_OPTION = PresetDisplayOptionEnum.NONE
    DEFAULT_NOTE = 36
    PRESET_CHANGER = ClipNotePresetChanger
