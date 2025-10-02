from _Framework.SubjectSlot import SlotManager

from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface
from protocol0.domain.live_set.LiveSet import LiveSet


class ActionGroupMC6Pro(ActionGroupInterface, SlotManager):
    CHANNEL = 12

    def configure(self) -> None:
        self.add_encoder(
            identifier=1,
            name="capture midi",
            on_press=lambda: self._container.get(LiveSet).capture_midi(),
        )

    def launch_drop(self) -> None:
        from protocol0.shared.logging.Logger import Logger

        Logger.dev("launch drop")
        pass
