from functools import partial

from _Framework.SubjectSlot import SlotManager

from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface
from protocol0.domain.live_set.LiveSetInstruments import scrub_clips
from protocol0.domain.lom.clip.MidiClip import MidiClip
from protocol0.domain.lom.note.Note import Note
from protocol0.domain.shared.backend.Backend import Backend
from protocol0.shared.Song import Song


class ActionGroupLaunchPadPro(ActionGroupInterface, SlotManager):
    CHANNEL = 10

    def configure(self) -> None:
        for i in range(1, 9):
            self.add_encoder(
                identifier=i,
                name=f"test {i}",
                on_press=partial(scrub_clips, i),
            )

        self.add_encoder(identifier=9, name="analyze key", on_press=self.action_analyze_key)

    def action_analyze_key(self) -> None:
        import logging

        logging.getLogger(__name__).info("Analyzing key")
        clip = Song.selected_clip(MidiClip)
        notes = [Note.from_live_note(live_note) for live_note in clip.get_notes()]
        notes_dict = [note.to_dict() for note in notes]
        Backend.client().post_analyze_key(notes_dict)
