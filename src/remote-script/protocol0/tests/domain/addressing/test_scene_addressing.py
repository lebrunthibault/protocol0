import pytest

from protocol0.domain.lom.addressing.scene import resolve_scene
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.shared.Song import Song
from protocol0.tests.domain.fixtures.p0 import drain


def _create_scenes(p0, count: int) -> None:
    for _ in range(count):
        p0.song().create_scene(-1)  # appends and selects
    drain()  # flush the deferred remap so the wrappers exist


def test_sel_is_the_selected_scene(p0):
    _create_scenes(p0, 1)
    assert resolve_scene("SEL") == Song.selected_scene()
    assert resolve_scene("SEL").index == 1


def test_last(p0):
    _create_scenes(p0, 2)
    assert resolve_scene("LAST").index == len(Song.scenes()) - 1


def test_by_index_one_based(p0):
    _create_scenes(p0, 1)
    assert resolve_scene("2").index == 1


def test_index_out_of_range(p0):
    with pytest.raises(Protocol0Warning):
        resolve_scene("9")


def test_relative_scrolling_clamped(p0):
    _create_scenes(p0, 1)  # 2 scenes, scene 2 selected
    assert resolve_scene("<").index == 0
    assert resolve_scene(">").index == 1  # clamped at the last scene
