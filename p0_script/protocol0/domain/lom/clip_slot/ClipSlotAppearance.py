import Live


class ClipSlotAppearance(object):
    def __init__(self, live_clip_slot: Live.ClipSlot.ClipSlot) -> None:
        self._live_clip_slot = live_clip_slot

    @property
    def has_stop_button(self) -> bool:
        return self._live_clip_slot and self._live_clip_slot.has_stop_button

    @has_stop_button.setter
    def has_stop_button(self, has_stop_button: bool) -> None:
        if self._live_clip_slot:
            self._live_clip_slot.has_stop_button = has_stop_button

    def refresh(self) -> None:
        pass
        # we never use clip slot stop buttons
        # if self.has_stop_button:
        #     self.has_stop_button = False
