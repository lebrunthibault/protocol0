from protocol0.application.http import HttpServer
from protocol0.domain.lom.song.components.TrackCrudComponent import TrackCrudComponent
from protocol0.shared.Song import Song


def test_create_midi_track_headless(p0, tick_scheduler):
    """End-to-end proof of the mutating fakes: the Sequence returned by the CRUD
    component terminates because the fake song fired the tracks listeners."""
    crud = HttpServer.get_container().get(TrackCrudComponent)
    initial_count = len(list(Song.simple_tracks()))

    seq = crud.create_midi_track(initial_count)
    tick_scheduler.drain()

    assert seq.state.terminated
    assert len(list(Song.simple_tracks())) == initial_count + 1


def test_delete_track_headless(p0, tick_scheduler):
    crud = HttpServer.get_container().get(TrackCrudComponent)
    initial_count = len(list(Song.simple_tracks()))

    seq = crud.create_midi_track(initial_count)
    tick_scheduler.drain()
    assert len(list(Song.simple_tracks())) == initial_count + 1

    seq = crud.delete_track(initial_count)
    tick_scheduler.drain()

    assert seq.state.terminated
    assert len(list(Song.simple_tracks())) == initial_count


def test_duplicate_track_headless(p0, tick_scheduler):
    crud = HttpServer.get_container().get(TrackCrudComponent)
    initial_count = len(list(Song.simple_tracks()))
    source = list(Song.simple_tracks())[0]

    seq = crud.duplicate_track(source)
    tick_scheduler.drain()

    assert seq.state.terminated
    tracks = list(Song.simple_tracks())
    assert len(tracks) == initial_count + 1
    assert tracks[1].name == source.name
