from typing import Optional

from protocol0.domain.live_set.LiveSet import LiveTrack
from protocol0.domain.lom.SessionRing import get_session_ring_scene_offset
from protocol0.domain.lom.clip.MidiClip import MidiClip
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning


def change_track_sound(track_type: str, sound_index: int) -> None:
    live_track = LiveTrack[track_type]
    track = live_track.get()

    if not live_track.uses_simpler():
        raise Protocol0Warning("Track doesn't use simpler")

    scene_offset = get_session_ring_scene_offset()

    for clip_slot in track.clip_slots[scene_offset : scene_offset + 8]:  # noqa
        clip: Optional[MidiClip] = clip_slot.clip
        if not clip:
            continue

        notes = clip.get_live_notes()

        lowest_pitch = min(note.pitch for note in notes) if notes else 0

        for note in notes:
            if note.pitch == lowest_pitch:
                note.pitch = sound_index - 1 + 36  # offset a C1

        clip.apply_note_modifications(notes)
