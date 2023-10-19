from typing import Optional

from protocol0.domain.lom.clip.MidiClip import MidiClip
from protocol0.domain.lom.device.DrumRackDevice import DrumRackDevice
from protocol0.domain.lom.instrument.preset.preset_changer.PresetChangerInterface import (
    PresetChangerInterface,
)
from protocol0.domain.shared.ApplicationView import ApplicationView
from protocol0.domain.shared.ValueScroller import ValueScroller
from protocol0.shared.Song import Song


class ClipNotePresetChanger(PresetChangerInterface):
    _DECREMENT_CC = 54
    _INCREMENT_CC = 55

    def scroll(self, go_next: bool) -> None:
        # manually transpose the selected clip
        clip: Optional[MidiClip] = (
            Song.selected_track().clip_slots[Song.selected_scene().index].clip
        )
        if clip is None:
            return

        notes = clip.get_notes()
        clip_pitches = list(set([note.pitch for note in notes if not note.muted]))
        from protocol0.shared.logging.Logger import Logger
        Logger.dev((notes, clip_pitches))
        if len(clip_pitches) != 1:
            Logger.warning("Multiple pitches detected in clip")
            ApplicationView.show_clip()
            return

        drum_rack = Song.selected_track().instrument.device
        assert isinstance(drum_rack, DrumRackDevice), "Expected drum rack device"

        pad_pitches = [pad.note for pad in drum_rack.filled_drum_pads]

        next_pitch = ValueScroller.scroll_values(pad_pitches, clip_pitches[0], go_next, rotate=False)

        for note in notes:
            if not note.muted:
                note.pitch = next_pitch

        clip.set_notes(notes, replace=True)
