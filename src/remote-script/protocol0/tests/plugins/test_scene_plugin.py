from protocol0.application.plugin.PluginLoader import PluginLoader
from protocol0.plugins.ScenePlugin import ScenePlugin
from protocol0.shared.Song import Song
from protocol0.tests.domain.fixtures.http import dispatch_action
from protocol0.tests.domain.fixtures.p0 import drain


def _plugin(p0) -> ScenePlugin:
    return PluginLoader.get(ScenePlugin)


def _create_scenes(p0, count: int) -> None:
    for _ in range(count):
        p0.song().create_scene(-1)
    drain()


def test_fire(p0):
    song = p0.song()
    _plugin(p0).fire()
    assert song.scenes[0].is_triggered is True


def test_select_by_index(p0):
    song = p0.song()
    _create_scenes(p0, 1)  # scene 2 selected
    _plugin(p0).select(scene="1")
    assert song.view.selected_scene is song.scenes[0]


def test_scroll(p0):
    song = p0.song()
    _create_scenes(p0, 1)
    _plugin(p0).select(scene="1")
    _plugin(p0).scroll(direction=">")
    assert song.view.selected_scene is song.scenes[1]


def test_create_through_http(p0, tick_scheduler):
    initial_count = len(Song.scenes())

    response = dispatch_action("/api/action/scene/create", {}, tick_scheduler)

    assert response.code == 200
    assert response.json["status"] == "done"
    assert len(Song.scenes()) == initial_count + 1


def test_duplicate(p0):
    initial_count = len(Song.scenes())
    _plugin(p0).duplicate(scene="1")
    drain()
    assert len(Song.scenes()) == initial_count + 1


def test_delete(p0):
    _create_scenes(p0, 1)
    initial_count = len(Song.scenes())
    _plugin(p0).delete(scene="LAST")
    drain()
    assert len(Song.scenes()) == initial_count - 1
