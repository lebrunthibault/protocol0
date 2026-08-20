from unittest.mock import Mock

from protocol0.domain.lom.clip.MidiClip import MidiClip
from protocol0.domain.lom.note.Note import Note


def make_clip(notes):
    """A MidiClip whose note reading/writing is stubbed.

    ``remove_muted_notes`` is pure orchestration on top of ``get_all_notes`` and
    ``replace_notes``; stubbing both keeps the test off the Live API (the clip
    fixture stubs neither ``add_new_notes`` nor ``remove_notes_extended``).
    """
    clip = MidiClip.__new__(MidiClip)  # no __init__: it wires Live listeners
    clip.get_all_notes = Mock(return_value=notes)
    clip.replace_notes = Mock()
    return clip


def note(pitch, muted):
    return Note(pitch=pitch, start=0, duration=1, velocity=100, mute=muted)


def test_remove_muted_notes_keeps_only_the_unmuted_ones():
    kept, dropped = note(60, False), note(62, True)
    clip = make_clip([kept, dropped])

    clip.remove_muted_notes()

    clip.replace_notes.assert_called_once_with([kept])


def test_remove_muted_notes_does_not_rewrite_the_clip_when_nothing_is_muted():
    clip = make_clip([note(60, False), note(62, False)])

    assert clip.remove_muted_notes() is None
    clip.replace_notes.assert_not_called()


def test_remove_muted_notes_on_an_empty_clip_is_a_no_op():
    clip = make_clip([])

    assert clip.remove_muted_notes() is None
    clip.replace_notes.assert_not_called()


def test_remove_muted_notes_ignores_the_note_selection():
    # get_all_notes (not get_notes) is the reader: get_notes narrows to the
    # selected notes, and replace_notes wipes the whole clip -> feeding it a
    # selection would delete every unselected note.
    clip = make_clip([note(60, True)])
    clip.get_notes = Mock(side_effect=AssertionError("must not read the selection"))

    clip.remove_muted_notes()

    clip.get_all_notes.assert_called_once_with()
    clip.replace_notes.assert_called_once_with([])
