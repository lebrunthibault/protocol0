from functools import partial

from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface
from protocol0.domain.lom.device_parameter.DeviceParamEnum import DeviceParamEnum
from protocol0.shared.Song import Song


class ActionGroupDiva(ActionGroupInterface):
    CHANNEL = 12

    def configure(self) -> None:
        def scroll_parameter(device_param_enum: DeviceParamEnum, go_next: bool) -> None:
            instrument = Song.selected_or_soloed_track().instrument
            assert instrument, "selected or soloed track has no instrument"

            parameter = instrument.device.get_parameter_by_name(device_param_enum)

            if not parameter:
                return None

            parameter.scroll(go_next)

        for i, param_enum in enumerate(
            [
                DeviceParamEnum.DIVA_FILTER_FREQ,
                DeviceParamEnum.DIVA_FILTER_ENV,
                DeviceParamEnum.DIVA_FILTER_RES,
                DeviceParamEnum.DIVA_OUTPUT,
            ]
        ):
            self.add_encoder(
                identifier=i + 1,
                name=f"encoder {i + 1}",
                on_scroll=partial(scroll_parameter, param_enum),
            )
