from protocol0.application.http.HttpServer import get_container
from protocol0.application.http.Router import route
from protocol0.domain.lom.set.AbletonSet import AbletonSet


@route("GET", "/set/get_state")
def get_state() -> None:
    get_container().get(AbletonSet).notify(force=True)
