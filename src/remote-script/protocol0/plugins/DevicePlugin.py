"""Device actions — a plugin made of a single ``@action`` for now.

This is a real, enabled action (not a template): it powers the ``load_device``
shortcut via ``POST /api/action/device/load_device``. It also demonstrates the
**single-file drop-in** form — a plugin can be one ``.py`` file dropped directly
under ``plugins/``, with no package or ``__init__.py``.
"""
from protocol0.application.http.HttpServer import get_container
from protocol0.application.plugin.PluginInterface import PluginInterface
from protocol0.application.plugin.action import action
from protocol0.domain.lom.device.DeviceService import DeviceService


class DevicePlugin(PluginInterface):
    name = "device"

    @action
    def load_device(self, name: str) -> None:
        """Load a device (instrument or audio effect) onto the selected track by name."""
        get_container().get(DeviceService).load_device(name)
