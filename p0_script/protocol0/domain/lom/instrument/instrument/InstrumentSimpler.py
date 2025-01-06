from typing import cast, Any

from protocol0.domain.lom.device.SimplerDevice import SimplerDevice
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface
from protocol0.domain.lom.instrument.preset.PresetDisplayOptionEnum import PresetDisplayOptionEnum
from protocol0.shared.Config import Config


class InstrumentSimpler(InstrumentInterface):
    NAME = "Simpler"
    PRESETS_PATH = Config.SAMPLE_DIRECTORY
    PRESET_DISPLAY_OPTION = PresetDisplayOptionEnum.CATEGORY

    def __init__(self, *a: Any, **k: Any) -> None:
        super(InstrumentSimpler, self).__init__(*a, **k)
        self.device = cast(SimplerDevice, self.device)
