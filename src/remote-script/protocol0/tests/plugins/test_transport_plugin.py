import pytest

from protocol0.application.plugin.PluginLoader import PluginLoader
from protocol0.plugins.TransportPlugin import TransportPlugin
from protocol0.tests.domain.fixtures.http import dispatch_action


def _plugin(p0) -> TransportPlugin:
    return PluginLoader.get(TransportPlugin)


def test_metronome_toggle(p0):
    song = p0.song()
    _plugin(p0).metronome("TGL")
    assert song.metronome is True
    _plugin(p0).metronome("OFF")
    assert song.metronome is False


def test_tempo_absolute_and_steps(p0):
    song = p0.song()
    _plugin(p0).tempo("124")
    assert song.tempo == 124
    _plugin(p0).tempo(">5")
    assert song.tempo == 129
    _plugin(p0).tempo("<")
    assert song.tempo == 128


def test_clip_trigger_quantization_by_name_and_cycling(p0):
    song = p0.song()
    _plugin(p0).clip_trigger_quantization("bar")
    assert song.clip_trigger_quantization == 4
    _plugin(p0).clip_trigger_quantization(">")
    assert song.clip_trigger_quantization == 5  # half
    _plugin(p0).clip_trigger_quantization("none")
    assert song.clip_trigger_quantization == 0


def test_midi_recording_quantization(p0):
    song = p0.song()
    _plugin(p0).midi_recording_quantization("sixteenth")
    assert song.midi_recording_quantization == 5


def test_session_record(p0):
    song = p0.song()
    _plugin(p0).session_record("ON")
    assert song.session_record is True


def test_undo_redo(p0):
    song = p0.song()
    _plugin(p0).undo()
    _plugin(p0).redo()
    assert song.undone == 1
    assert song.redone == 1


def test_playback_start_and_stop(p0, tick_scheduler):
    song = p0.song()
    _plugin(p0).start_playback()
    assert song.is_playing is True

    seq = _plugin(p0).stop_playback()
    tick_scheduler.drain()
    assert song.is_playing is False
    assert seq.state.terminated


def test_tempo_through_http(p0, tick_scheduler):
    response = dispatch_action("/api/action/transport/tempo", {"value": "140"}, tick_scheduler)

    assert response.code == 200
    assert response.json["status"] == "done"
    assert p0.song().tempo == 140


def test_invalid_quantization_is_a_clean_error(p0, tick_scheduler):
    response = dispatch_action(
        "/api/action/transport/clip_trigger_quantization", {"value": "loud"}, tick_scheduler
    )

    assert response.code == 500
    assert response.json["status"] == "error"
    assert "invalid value" in response.json["error"]
