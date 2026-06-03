from protocol0.application.http.HttpServer import get_container
from protocol0.application.http.Router import api_route
from protocol0.domain.lom.device.DeviceService import DeviceService


@api_route("POST", "/device/load")
def load_device(name: str) -> None:
    """Load a device (instrument or audio effect) onto the selected track by name."""
    get_container().get(DeviceService).load_device(name, True)
