from protocol0.application.plugin.PluginLoader import PluginLoader
from protocol0.plugins.ArrangementPlugin import ArrangementPlugin
from protocol0.tests.domain.fixtures.http import dispatch
from protocol0.tests.domain.fixtures.p0 import drain


def _plugin(p0) -> ArrangementPlugin:
    return PluginLoader.get(ArrangementPlugin)


def _midi_track_with_clip(p0, name: str = "Midi"):
    song = p0.song()
    song.create_midi_track(None)
    fake_track = song.view.selected_track
    fake_track.name = name
    fake_track.clip_slots[0].add_clip()
    drain()
    return fake_track


def test_duplicate_clip_to_arrangement(p0):
    fake_track = _midi_track_with_clip(p0)

    _plugin(p0).duplicate_clip(time=16.0)

    assert fake_track.arrangement_clips == [fake_track.clip_slots[0].clip]


def test_clear_arrangement(p0):
    fake_track = _midi_track_with_clip(p0)
    _plugin(p0).duplicate_clip(time=16.0)

    _plugin(p0).clear()

    assert fake_track.arrangement_clips == []


def test_set_time(p0):
    _plugin(p0).set_time(time=32.0)
    assert p0.song().current_song_time == 32.0


def test_add_locator(p0):
    song = p0.song()

    _plugin(p0).add_locator(time=8.0)
    drain()
    assert [cue.time for cue in song.cue_points] == [8.0]

    # a second call at the same time is a no-op (the facade only creates)
    _plugin(p0).add_locator(time=8.0)
    drain()
    assert [cue.time for cue in song.cue_points] == [8.0]


def test_get_state_carries_targeting_fields(p0, tick_scheduler):
    _midi_track_with_clip(p0, "Lead")

    response = dispatch("GET", "/api/set/get_state", {}, tick_scheduler)

    assert response.code == 200
    state = response.json
    assert state["selected_track"]["name"] == "Lead"
    assert state["selected_track"]["type"] == "midi"
    assert {"index", "live_id", "muted", "solo", "armed", "devices"} <= set(
        state["selected_track"]
    )
    assert state["tempo"] == 120
    assert isinstance(state["scenes"], list)
