from _Framework.Util import find_if

from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface

# noinspection SpellCheckingInspection
from protocol0.domain.lom.set.LiveSet import LiveSet


class ActionGroupLive3(ActionGroupInterface):
    CHANNEL = 3

    def configure(self) -> None:
        self.add_encoder(
            identifier=16 + 5,
            name="copy piano to bass",
            on_press=lambda: self._container.get(LiveSet).copy_piano_to_bass,
        )
