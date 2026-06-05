from protocol0.application.http.Router import api_route
from protocol0.shared.Song import Song


@api_route("POST", "/song/toggle_follow")
def toggle_follow_song() -> None:
    """Stop following the playhead in the arrangement view."""
    Song.view().follow_song = False
