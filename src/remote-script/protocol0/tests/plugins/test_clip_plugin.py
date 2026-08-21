import pytest

from protocol0.application.plugin.PluginLoader import PluginLoader
from protocol0.plugins.ClipPlugin import ClipPlugin
from protocol0.tests.domain.fixtures.http import dispatch_action
from protocol0.tests.domain.fixtures.p0 import drain

from Live.Clip import MidiNoteSpecification


def _plugin(p0) -> ClipPlugin:
    return PluginLoader.get(ClipPlugin)


def _midi_track_with_clip(p0, name: str = "Midi"):
    song = p0.song()
    song.create_midi_track(None)
    fake_track = song.view.selected_track
    fake_track.name = name
    fake_track.clip_slots[0].add_clip()
    drain()
    return fake_track


def _note(pitch: int, start: float = 0.0, duration: float = 1.0, mute: bool = False):
    return MidiNoteSpecification(
        pitch=pitch, start_time=start, duration=duration, velocity=100, mute=mute
    )


def test_fire_and_stop(p0):
    fake_track = _midi_track_with_clip(p0)
    fake_clip = fake_track.clip_slots[0].clip

    _plugin(p0).fire()
    assert fake_clip.is_playing is True

    _plugin(p0).stop()
    assert fake_clip.is_playing is False


def test_loop_toggle(p0):
    fake_clip = _midi_track_with_clip(p0).clip_slots[0].clip
    _plugin(p0).loop()
    assert fake_clip.looping is False


def test_mute(p0):
    fake_clip = _midi_track_with_clip(p0).clip_slots[0].clip
    _plugin(p0).mute(value="ON")
    assert fake_clip.muted is True


def test_add_note(p0, tick_scheduler):
    fake_clip = _midi_track_with_clip(p0).clip_slots[0].clip

    _plugin(p0).add_note(pitch=60, start=0.0, duration=1.0)
    drain()

    assert len(fake_clip._notes) == 1
    assert fake_clip._notes[0].pitch == 60


def test_transpose(p0):
    fake_clip = _midi_track_with_clip(p0).clip_slots[0].clip
    fake_clip._notes.append(_note(60))

    _plugin(p0).transpose(semitones=2)
    drain()

    assert [note.pitch for note in fake_clip._notes] == [62]


def test_clear_notes(p0):
    fake_clip = _midi_track_with_clip(p0).clip_slots[0].clip
    fake_clip._notes.extend([_note(60), _note(64)])

    _plugin(p0).clear_notes()
    drain()

    assert fake_clip._notes == []


def test_remove_muted_notes(p0):
    fake_clip = _midi_track_with_clip(p0).clip_slots[0].clip
    fake_clip._notes.extend([_note(60), _note(64, mute=True)])

    _plugin(p0).remove_muted_notes()
    drain()

    assert [note.pitch for note in fake_clip._notes] == [60]


def test_create_clip_in_empty_slot(p0):
    song = p0.song()
    song.create_midi_track(None)
    fake_track = song.view.selected_track
    fake_track.name = "Empty"
    drain()

    _plugin(p0).create()
    drain()

    assert fake_track.clip_slots[0].has_clip is True


def test_delete_clip(p0):
    fake_track = _midi_track_with_clip(p0)

    _plugin(p0).delete()
    drain()

    assert fake_track.clip_slots[0].clip is None


def test_add_note_through_http(p0, tick_scheduler):
    fake_clip = _midi_track_with_clip(p0).clip_slots[0].clip

    response = dispatch_action(
        "/api/action/clip/add_note",
        {"pitch": 60, "start": 0.0, "duration": 1.0},
        tick_scheduler,
    )

    assert response.code == 200
    assert response.json["status"] == "done"
    assert len(fake_clip._notes) == 1


def test_midi_action_on_audio_clip_is_a_clean_error(p0, tick_scheduler):
    song = p0.song()
    song.create_audio_track(None)
    fake_track = song.view.selected_track
    fake_track.name = "Audio"
    fake_track.clip_slots[0].add_clip()
    fake_track.clip_slots[0].clip.is_audio_clip = True
    drain()

    response = dispatch_action("/api/action/clip/clear_notes", {}, tick_scheduler)

    assert response.code == 500
    assert "not a MIDI clip" in response.json["error"]
