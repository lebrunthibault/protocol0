from functools import partial

import Live

from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.instrument.InstrumentLoadedEvent import InstrumentLoadedEvent
from protocol0.domain.shared.ApplicationView import ApplicationView
from protocol0.domain.shared.BrowserServiceInterface import BrowserServiceInterface
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.infra.interface.BrowserLoaderService import BrowserLoaderService
from protocol0.shared.sequence.Sequence import Sequence


class BrowserService(BrowserServiceInterface):
    def __init__(
        self, browser: Live.Browser.Browser, browser_loader_service: BrowserLoaderService
    ) -> None:
        super(BrowserService, self).__init__()
        self._browser = browser
        self._browser_loader_service = browser_loader_service

    def load_device_from_enum(self, device_enum: DeviceEnum) -> Sequence:
        seq = Sequence()
        browser_name = device_enum.browser_name
        if (
            browser_name.endswith(".adv")
            or browser_name.endswith(".adg")
            or browser_name.endswith(".vstpreset")
        ):
            load_func = partial(self._browser_loader_service.load_from_user_library, browser_name)
        else:
            load_func = partial(self._browser_loader_service.load_device, browser_name)

        seq.add(load_func)
        seq.wait(20)
        seq.add(ApplicationView.focus_detail)
        if device_enum.is_instrument:
            seq.add(partial(DomainEventBus.emit, InstrumentLoadedEvent(device_enum)))
        return seq.done()

    def load_sample(self, name: str) -> Sequence:
        self._browser_loader_service.load_sample(name)
        seq = Sequence()
        seq.wait(10)
        return seq.done()

    def load_from_user_library(self, name: str) -> Sequence:
        self._browser_loader_service.load_from_user_library(name)
        seq = Sequence()
        seq.wait(20)
        return seq.done()
