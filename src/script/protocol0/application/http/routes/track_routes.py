from protocol0.application.http.Router import route
from protocol0.shared.Song import Song, find_track


@route("GET", "/track/select")
def select_track(name: str) -> None:
    """Select a track by name (use "master" to select the master track)."""
    if name.lower() == "master":
        Song.master_track().select()
    else:
        find_track(name).select()
