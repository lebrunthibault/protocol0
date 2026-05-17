from protocol0.application.http.HttpServer import get_container
from protocol0.application.http.Router import route
from protocol0.domain.live_set.LiveSet import LiveSet


@route("GET", "/clip/key_detected")
def on_key_detected(pitch: int) -> None:
    get_container().get(LiveSet).on_key_detected(pitch)
