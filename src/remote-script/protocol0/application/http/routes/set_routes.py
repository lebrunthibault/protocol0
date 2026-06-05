from dataclasses import asdict

from protocol0.application.http.HttpServer import get_container
from protocol0.application.http.Router import api_route
from protocol0.domain.lom.set.AbletonSet import AbletonSet


@api_route("GET", "/set/get_state")
def get_state() -> dict:
    """Return the full serialized state of the current Ableton set as JSON."""
    return asdict(get_container().get(AbletonSet).to_model(full=True))
