from protocol0.application.http.HttpServer import get_container
from protocol0.application.http.Router import route
from protocol0.domain.audit.LogService import LogService
from protocol0.domain.audit.SongStatsService import SongStatsService


@route("GET", "/log/selected")
def log_selected() -> None:
    get_container().get(LogService).log_current()


@route("GET", "/log/song_stats")
def log_song_stats() -> None:
    get_container().get(SongStatsService).display_song_stats()
