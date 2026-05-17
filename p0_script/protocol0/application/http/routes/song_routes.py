from protocol0.application.http.HttpServer import get_container
from protocol0.application.http.Router import route
from protocol0.domain.lom.song.components.PlaybackComponent import PlaybackComponent
from protocol0.shared.Song import Song


@route("GET", "/song/play_pause")
def play_pause() -> None:
    get_container().get(PlaybackComponent).play_pause()


@route("GET", "/song/toggle_follow")
def toggle_follow_song() -> None:
    Song.view().follow_song = False
