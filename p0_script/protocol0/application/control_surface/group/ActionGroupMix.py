from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface
from protocol0.domain.lom.set.MixingService import MixingService


class ActionGroupClip(ActionGroupInterface):
    CHANNEL = 13

    def configure(self) -> None:
        # DUPLicate clip
        self.add_encoder(
            identifier=1,
            name="log mix state",
            on_press=self._container.get(MixingService).log_state,
        )
