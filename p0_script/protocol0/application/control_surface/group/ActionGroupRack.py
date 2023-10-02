from functools import partial

from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface
from protocol0.domain.lom.instrument.instrument.InstrumentService import InstrumentService


class ActionGroupRack(ActionGroupInterface):
    CHANNEL = 2

    def configure(self) -> None:
        # RACK macro control encoders
        instrument_service = self._container.get(InstrumentService)

        for i in range(1, 9):
            self.add_encoder(
                identifier=i, name=f"edit macro control {i}",
                on_press=partial(instrument_service.toggle_macro_control, i),
                on_scroll=partial(instrument_service.scroll_macro_control, i)
            )
