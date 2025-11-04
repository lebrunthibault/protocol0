from typing import List

from protocol0.domain.lom.clip_slot.MidiClipSlot import MidiClipSlot
from protocol0.domain.lom.note.Note import Note
from protocol0.shared.Song import Song


def split_bar_notes(clip_slot: MidiClipSlot) -> None:
    loop = clip_slot.clip.loop

    # do this on the whole clip
    loop_start = loop.start
    loop.start = 0
    live_notes = clip_slot.clip.get_notes()

    if not live_notes:
        return

    notes = [Note.from_live_note(live_note) for live_note in live_notes]
    split_notes = split_notes_to_beats(notes)

    clip_slot.clip.replace_notes(split_notes)
    loop.start = loop_start


def quantize_bar_notes(clip_slot: MidiClipSlot) -> None:
    import logging

    logging.getLogger(__name__).info("quantizing bar notes")
    loop = clip_slot.clip.loop

    # do this on the whole clip
    loop_start = loop.start
    loop.start = 0
    live_notes = clip_slot.clip.get_notes()

    if not live_notes:
        return

    for live_note in live_notes:
        if 3.75 < live_note.start_time % 4:
            live_note.start_time = round(live_note.start_time)

    clip_slot.clip.apply_note_modifications(live_notes)
    loop.start = loop_start


def make_clip_monophonic(clip_slot: MidiClipSlot) -> None:
    import logging

    logging.getLogger(__name__).info(clip_slot)
    clip_slot.clip.quantize()
    loop = clip_slot.clip.loop

    # do this on the whole clip
    loop_start = loop.start
    loop.start = 0

    live_notes = clip_slot.clip.get_notes()
    if not live_notes:
        return

    notes = [Note.from_live_note(live_note) for live_note in live_notes]
    import logging

    logging.getLogger(__name__).info(notes)

    # Filter notes: keep only those with pitch <= C2 (MIDI note 36)
    bass_notes = [note for note in notes if note.pitch <= 48]

    if not bass_notes:
        return

    # Sort notes by start time for legato processing
    bass_notes.sort(key=lambda n: n.start)

    # # Make notes legato (connect them with no gaps) and clamp to C1-C2 range
    for i, note in enumerate(bass_notes):
        # Map pitch to C1-C2 range (36-48) preserving note name

        if note.pitch != 48:
            # Get note within octave (0-11), then map to C1-C2 range
            note_in_octave = note.pitch % 12
            note.pitch = 36 + note_in_octave  # C1 is 36, so add the note offset

        # Make legato: extend duration to next note's start time
        if i < len(bass_notes) - 1:
            next_note_start = bass_notes[i + 1].start
            if next_note_start > note.start:
                note.duration = next_note_start - note.start
        else:
            # Last note: extend to end of clip
            note.end = clip_slot.clip.end_marker

    split_notes = split_notes_to_beats(bass_notes)
    clip_slot.clip.replace_notes(split_notes)

    loop.start = loop_start


def split_notes_to_beats(notes: List[Note]) -> List[Note]:
    """Split notes into bars: each note should not exceed one bar in length."""
    bar_length = Song.signature_numerator()
    split_notes = []

    for note in notes:
        note_bar_start = int(note.start / bar_length) * bar_length
        note_bar_end = note_bar_start + bar_length

        if note.end <= note_bar_end:
            # Note fits within one bar
            split_notes.append(note)
        else:
            # Note spans multiple bars, split it
            current_start = note.start
            while current_start < note.end:
                current_bar_end = int(current_start / bar_length) * bar_length + bar_length
                split_note_end = min(note.end, current_bar_end)

                split_note = Note(
                    pitch=note.pitch,
                    start=current_start,
                    duration=split_note_end - current_start,
                    velocity=note.velocity,
                )
                split_notes.append(split_note)
                current_start = current_bar_end

    return split_notes
