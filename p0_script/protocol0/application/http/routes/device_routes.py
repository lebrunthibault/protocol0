from protocol0.application.http.HttpServer import get_container
from protocol0.application.http.Router import route
from protocol0.domain.lom.device.DeviceService import DeviceService


@route("GET", "/device/load")
def load_device(name: str) -> None:
    get_container().get(DeviceService).load_device(name, True)
