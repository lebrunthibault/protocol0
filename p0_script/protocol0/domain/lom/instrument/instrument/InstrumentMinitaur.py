from protocol0.domain.lom.instrument.InstrumentColorEnum import InstrumentColorEnum
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface


class InstrumentMinitaur(InstrumentInterface):
    NAME = "Minitaur"
    PRESET_EXTENSION = ".syx"
    TRACK_COLOR = InstrumentColorEnum.MINITAUR
    INSTRUMENT_TRACK_NAME = "Bass"
    CAN_BE_SHOWN = False
    PRESETS_PATH = (
        "C:\\Users\\thiba\\AppData\\Roaming\\Moog Music Inc\\Minitaur\\Presets Library\\User"
    )
