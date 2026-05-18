from typing import cast, Any

from protocol0.domain.lom.device.SimplerDevice import SimplerDevice
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface


class InstrumentSimpler(InstrumentInterface):
    NAME = "Simpler"

    def __init__(self, *a: Any, **k: Any) -> None:
        super(InstrumentSimpler, self).__init__(*a, **k)
        self.device = cast(SimplerDevice, self.device)
