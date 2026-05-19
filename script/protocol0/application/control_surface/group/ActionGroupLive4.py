from functools import partial

from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface
from protocol0.domain.live_set.LiveSetInstruments import (
    move_clip_loop,
    change_clip_loop,
    sync_markers,
)
from protocol0.domain.lom.clip.MidiClip import MidiClip
from protocol0.shared.Song import Song


class ActionGroupLive4(ActionGroupInterface):
    CHANNEL = 4

    def configure(self) -> None:
        self.add_encoder(
            identifier=4, name="move clip loop", on_scroll=move_clip_loop, on_press=sync_markers
        )
        self.add_encoder(identifier=5, name="clip loop 1", on_press=partial(change_clip_loop, 1))
        self.add_encoder(identifier=6, name="clip loop 2", on_press=partial(change_clip_loop, 2))
        self.add_encoder(identifier=7, name="clip loop 4", on_press=partial(change_clip_loop, 4))
        self.add_encoder(identifier=8, name="clip loop 8", on_press=partial(change_clip_loop, 8))
        self.add_encoder(identifier=9, name="clip loop 16", on_press=partial(change_clip_loop, 16))

        self.add_encoder(identifier=16, name="test", on_press=self.action_test)

    def action_test(self) -> None:
        clip = Song.selected_clip(MidiClip)
        import logging

        logging.getLogger(__name__).info(clip.get_notes())
