from functools import partial

from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface
from protocol0.domain.lom.instrument.instrument.InstrumentService import InstrumentService


class ActionGroupRack(ActionGroupInterface):
    CHANNEL = 2

    def configure(self) -> None:
        # RACK macro control encoders
        scroll_macro_control = self._container.get(InstrumentService).scroll_macro_control

        for i in range(1, 9):
            self.add_encoder(
                identifier=i, name=f"scroll macro {i}", on_scroll=partial(scroll_macro_control, i)
            )
