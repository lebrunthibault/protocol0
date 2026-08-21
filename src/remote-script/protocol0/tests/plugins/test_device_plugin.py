import pytest

from protocol0.application.plugin.PluginLoader import PluginLoader
from protocol0.domain.lom.addressing.device import resolve_device
from protocol0.domain.shared.errors.Protocol0Warning import Protocol0Warning
from protocol0.plugins.DevicePlugin import DevicePlugin
from protocol0.shared.Song import Song, find_track
from protocol0.tests.domain.fixtures.device import (
    AbletonDevice,
    AbletonDeviceChain,
    AbletonRackDevice,
)
from protocol0.tests.domain.fixtures.device_parameter import AbletonDeviceParameter
from protocol0.tests.domain.fixtures.http import dispatch_action
from protocol0.tests.domain.fixtures.p0 import drain
from protocol0.tests.domain.fixtures.simple_track import AbletonTrack


def _plugin(p0) -> DevicePlugin:
    return PluginLoader.get(DevicePlugin)


def _track_with_devices(p0):
    """A track holding [EQ Eight, rack("My Rack" > "Chain 1" > Reverb)]."""
    song = p0.song()
    fake_track = AbletonTrack()
    fake_track.name = "Synths"
    eq = AbletonDevice("EQ Eight")
    eq.parameters.append(AbletonDeviceParameter("Dry/Wet", default_value=0.5))
    reverb = AbletonDevice("Reverb")
    chain = AbletonDeviceChain("Chain 1")
    chain.devices = [reverb]
    rack = AbletonRackDevice("My Rack")
    rack.chains = [chain]
    fake_track.devices = [eq, rack]
    song.tracks = song.tracks + [fake_track]
    song._sync_clip_slot_matrix()
    drain()
    return fake_track, eq, rack, reverb


def test_resolve_device_by_index_and_name(p0):
    _track_with_devices(p0)
    track = find_track("Synths")

    assert resolve_device(track, "1").name == "EQ Eight"
    assert resolve_device(track, "2").name == "My Rack"
    assert resolve_device(track, "reverb").name == "Reverb"  # found inside the rack


def test_resolve_device_dotted_rack_path(p0):
    _track_with_devices(p0)
    track = find_track("Synths")

    assert resolve_device(track, "2.1.1").name == "Reverb"


def test_resolve_device_dotted_path_errors(p0):
    _track_with_devices(p0)
    track = find_track("Synths")

    with pytest.raises(Protocol0Warning):
        resolve_device(track, "1.1.1")  # EQ Eight is not a rack
    with pytest.raises(Protocol0Warning):
        resolve_device(track, "2.9.1")  # no chain 9
    with pytest.raises(Protocol0Warning):
        resolve_device(track, "2.1")  # not rack.chain.device pairs


def test_toggle(p0):
    _, eq, _, _ = _track_with_devices(p0)

    _plugin(p0).toggle(track='"Synths"', device='"EQ Eight"', value="ON")
    assert eq.parameters[0].value == 1
    _plugin(p0).toggle(track='"Synths"', device='"EQ Eight"')
    assert eq.parameters[0].value == 0


def test_set_parameter_by_name(p0):
    _, eq, _, _ = _track_with_devices(p0)

    _plugin(p0).set_parameter(parameter="dry", value="75%", track='"Synths"', device="1")
    assert eq.parameters[1].value == pytest.approx(0.75)


def test_set_parameter_reset(p0):
    _, eq, _, _ = _track_with_devices(p0)
    eq.parameters[1].value = 0.9

    _plugin(p0).set_parameter(parameter="dry", value="RESET", track='"Synths"', device="1")
    assert eq.parameters[1].value == pytest.approx(0.5)


def test_delete_top_level_device(p0):
    fake_track, _, _, _ = _track_with_devices(p0)

    _plugin(p0).delete(track='"Synths"', device='"EQ Eight"')
    assert [device.name for device in fake_track.devices] == ["My Rack"]


def test_delete_device_inside_a_rack(p0):
    fake_track, _, rack, _ = _track_with_devices(p0)

    _plugin(p0).delete(track='"Synths"', device="2.1.1")
    assert rack.chains[0].devices == []


def test_select_through_http(p0, tick_scheduler):
    _track_with_devices(p0)

    response = dispatch_action(
        "/api/action/device/select", {"track": '"Synths"', "device": "1"}, tick_scheduler
    )

    assert response.code == 200
    assert response.json["status"] == "done"


def test_unknown_device_is_a_clean_error(p0, tick_scheduler):
    _track_with_devices(p0)

    response = dispatch_action(
        "/api/action/device/toggle", {"track": '"Synths"', "device": "nope"}, tick_scheduler
    )

    assert response.code == 500
    assert "no device matching" in response.json["error"]
