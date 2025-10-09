from functools import partial

from _Framework.SubjectSlot import SlotManager

from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface
from protocol0.domain.live_set.LiveSetInstruments import scrub_clips


class ActionGroupLaunchPadPro(ActionGroupInterface, SlotManager):
    CHANNEL = 10

    def configure(self) -> None:
        for i in range(1, 9):
            self.add_encoder(
                identifier=i,
                name=f"test {i}",
                on_press=partial(scrub_clips, i),
            )
