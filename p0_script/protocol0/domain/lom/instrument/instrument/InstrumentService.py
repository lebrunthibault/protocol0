from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger


class InstrumentService(object):
    _DEBUG = False

    def toggle_macro_control(self, index: int) -> None:
        rack_device = Song.selected_track().instrument_rack_device
        assert rack_device is not None, "No instrument rack device"

        param = rack_device.parameters[index]
        if param.value == param.min:
            param.value = param.max
        else:
            param.value = param.min

    def scroll_macro_control(self, index: int, go_next: bool) -> None:
        rack_device = Song.selected_track().instrument_rack_device
        assert rack_device is not None, "No instrument rack device"

        param = rack_device.parameters[index]
        if self._DEBUG:
            Logger.info((param.min, param.max, param.value, param.is_quantized))

        param.scroll(go_next)
