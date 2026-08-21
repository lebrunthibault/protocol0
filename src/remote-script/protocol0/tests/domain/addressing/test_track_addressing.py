import pytest

from protocol0.domain.lom.addressing.track import resolve_track
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.shared.Song import Song
from protocol0.tests.domain.fixtures.p0 import drain


def _add_named_tracks(p0, *names):
    song = p0.song()
    for name in names:
        song.create_midi_track(None)  # appends and selects the new track
        song.view.selected_track.name = name
    drain()  # flush the deferred remap so the wrappers exist


def test_sel_is_the_selected_track(p0):
    _add_named_tracks(p0, "Kick", "Bass")
    assert resolve_track("SEL").name == "Bass"
    assert resolve_track().name == "Bass"


def test_mst_is_the_master_track(p0):
    assert resolve_track("MST") == Song.master_track()


def test_by_index_one_based(p0):
    _add_named_tracks(p0, "Kick", "Bass")
    assert resolve_track("1").name == "First"  # the boot fixture track
    assert resolve_track("2").name == "Kick"
    assert resolve_track("3").name == "Bass"


def test_index_out_of_range(p0):
    with pytest.raises(Protocol0Warning):
        resolve_track("9")


def test_by_quoted_name_exact(p0):
    _add_named_tracks(p0, "Kick", "Kick 2")
    assert resolve_track('"Kick"').name == "Kick"


def test_quoted_name_requires_exact_match(p0):
    _add_named_tracks(p0, "Kick 2")
    with pytest.raises(Protocol0Warning):
        resolve_track('"Kick"')


def test_bare_name_falls_back_to_substring(p0):
    _add_named_tracks(p0, "Lead Synth")
    assert resolve_track("synth").name == "Lead Synth"


def test_relative_scrolling_clamped(p0):
    _add_named_tracks(p0, "Kick", "Bass")  # Bass selected (index 3)
    assert resolve_track("<").name == "Kick"
    assert resolve_track(">").name == "Bass"  # clamped at the last track


def test_unknown_name(p0):
    with pytest.raises(Protocol0Warning) as excinfo:
        resolve_track("nope")
    assert "no track matching" in str(excinfo.value)
