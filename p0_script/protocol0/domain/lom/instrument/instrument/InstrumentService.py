from protocol0.domain.lom.device.RackDevice import RackDevice
from protocol0.domain.shared.ValueScroller import ValueScroller
from protocol0.domain.shared.utils.utils import clamp
from protocol0.shared.Song import Song


class InstrumentService(object):
    def toggle_macro_control(self, index: int) -> None:
        device = Song.selected_device()
        assert isinstance(device, RackDevice), "Selected device is not a rack device"

        param = Song.selected_device().parameters[index]
        if param.value == param.min:
            param.value = param.max
        else:
            param.value = param.min

    def scroll_macro_control(self, index: int, go_next: bool) -> None:
        device = Song.selected_device()
        assert isinstance(device, RackDevice), "Selected device is not a rack device"

        param = Song.selected_device().parameters[index]
        from protocol0.shared.logging.Logger import Logger
        Logger.dev((param.min, param.max, param.value, param.is_quantized))

        if param.is_quantized:
            param.value = ValueScroller.scroll_values(list(param.value_items), param.value, go_next)
        else:
            step = (param.max - param.min) / 128
            new_value = param.value + (step if go_next else -step)
            param.value = clamp(new_value, param.min, param.max)
