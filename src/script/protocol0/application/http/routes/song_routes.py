from protocol0.application.http.Router import route
from protocol0.shared.Song import Song


@route("GET", "/song/toggle_follow")
def toggle_follow_song() -> None:
    """Stop following the playhead in the arrangement view."""
    Song.view().follow_song = False
