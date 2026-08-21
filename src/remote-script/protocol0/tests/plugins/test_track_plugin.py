import pytest

from protocol0.application.plugin.PluginLoader import PluginLoader
from protocol0.plugins.TrackPlugin import TrackPlugin
from protocol0.shared.Song import Song
from protocol0.tests.domain.fixtures.device_parameter import AbletonDeviceParameter
from protocol0.tests.domain.fixtures.http import dispatch_action
from protocol0.tests.domain.fixtures.p0 import drain
from protocol0.tests.domain.fixtures.simple_track import AbletonTrack


def _plugin(p0) -> TrackPlugin:
    return PluginLoader.get(TrackPlugin)


def _add_track(p0, name: str) -> AbletonTrack:
    song = p0.song()
    song.create_midi_track(None)
    fake = song.view.selected_track
    fake.name = name
    drain()  # flush the deferred remap so the wrappers exist
    return fake


def test_mute_by_quoted_name(p0):
    fake = _add_track(p0, "Kick")
    _plugin(p0).mute(track='"Kick"', value="ON")
    assert fake.mute is True


def test_solo_toggle_on_selected(p0):
    fake = _add_track(p0, "Bass")
    _plugin(p0).solo()
    assert fake.solo is True
    _plugin(p0).solo()
    assert fake.solo is False


def test_arm(p0):
    fake = _add_track(p0, "Vox")
    _plugin(p0).arm(value="ON")
    assert fake.arm is True


def test_monitor(p0):
    fake = _add_track(p0, "Vox")
    _plugin(p0).monitor(value="off")
    assert fake.current_monitoring_state == 2  # OFF
    _plugin(p0).monitor(value=">")
    assert fake.current_monitoring_state == 0  # wraps to IN


def test_rename(p0):
    _add_track(p0, "Old")
    _plugin(p0).rename(name="New")
    assert p0.song().view.selected_track.name == "New"


def test_volume_in_db(p0):
    fake = _add_track(p0, "Kick")
    _plugin(p0).volume("-6")
    track = Song.selected_track()
    assert track.volume == pytest.approx(-6, abs=0.1)
    assert fake.mixer_device.volume.value < 0.85


def test_pan(p0):
    fake = _add_track(p0, "Kick")
    _plugin(p0).pan("100%")
    assert fake.mixer_device.panning.value == 1.0
    _plugin(p0).pan("RESET")
    assert fake.mixer_device.panning.value == 0.0


def test_send_by_index(p0):
    song = p0.song()
    fake = AbletonTrack()
    fake.name = "Sendy"
    fake.mixer_device.sends.append(AbletonDeviceParameter("Send A"))
    song.tracks = song.tracks + [fake]  # fires the tracks listeners (remap)
    song._sync_clip_slot_matrix()
    drain()

    _plugin(p0).send(send="1", value="50%", track='"Sendy"')
    assert fake.mixer_device.sends[0].value == pytest.approx(0.5)


def test_fire_clip_in_scene(p0):
    fake = _add_track(p0, "Kick")
    fake.clip_slots[0].add_clip()
    drain()  # the ClipSlot wrapper maps its clip on the deferred has_clip listener
    _plugin(p0).fire(track='"Kick"', scene="1")
    assert fake.clip_slots[0].clip.is_playing is True


def test_stop_track(p0):
    fake = _add_track(p0, "Kick")
    fake.clip_slots[0].add_clip()
    fake.clip_slots[0].clip.is_playing = True
    _plugin(p0).stop(track='"Kick"')
    assert fake.clip_slots[0].clip.is_playing is False


def test_create_midi_through_http(p0, tick_scheduler):
    initial_count = len(list(Song.simple_tracks()))

    response = dispatch_action("/api/action/track/create_midi", {}, tick_scheduler)

    assert response.code == 200
    assert response.json["status"] == "done"
    assert len(list(Song.simple_tracks())) == initial_count + 1


def test_delete_through_http(p0, tick_scheduler):
    _add_track(p0, "Doomed")
    initial_count = len(list(Song.simple_tracks()))

    response = dispatch_action("/api/action/track/delete", {"track": '"Doomed"'}, tick_scheduler)

    assert response.code == 200
    assert len(list(Song.simple_tracks())) == initial_count - 1


def test_unknown_track_is_a_clean_error(p0, tick_scheduler):
    response = dispatch_action("/api/action/track/mute", {"track": "nope"}, tick_scheduler)

    assert response.code == 500
    assert "no track matching" in response.json["error"]
