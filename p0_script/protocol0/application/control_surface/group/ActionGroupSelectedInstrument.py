from functools import partial

from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface
from protocol0.shared.Song import Song


class ActionGroupSelectedInstrument(ActionGroupInterface):
    CHANNEL = 12

    def configure(self) -> None:
        def scroll_parameter(param_index: int, go_next: bool) -> None:
            instrument = Song.selected_or_soloed_track().instrument
            assert instrument, "selected or soloed track has no instrument"

            parameter = instrument.device.parameters[param_index + 1]
            parameter.scroll(go_next)

        for i in range(16):
            self.add_encoder(
                identifier=i + 1,
                name=f"encoder {i + 1}",
                on_scroll=partial(scroll_parameter, i),
            )
