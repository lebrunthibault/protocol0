from functools import partial
from typing import List, Optional

from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface
from protocol0.domain.lom.device_parameter.DeviceParamEnum import DeviceParamEnum
from protocol0.domain.lom.device_parameter.DeviceParameter import DeviceParameter
from protocol0.shared.Song import Song


class ActionGroupDiva(ActionGroupInterface):
    CHANNEL = 12

    def configure(self) -> None:
        def get_parameter(
            device_parameters: List[DeviceParameter],
            device_param_enum: DeviceParamEnum,
            param_position: int,
        ) -> Optional[DeviceParameter]:
            params = list(
                filter(
                    lambda p: p.name.lower() == device_param_enum.parameter_name.lower(),
                    device_parameters,
                )
            )

            assert len(params) > param_position, f"Cannot find {device_param_enum}"

            return params[param_position]

        def scroll_parameter(
            device_param_enum: DeviceParamEnum, param_position: int, go_next: bool
        ) -> None:
            instrument = Song.selected_or_soloed_track().instrument
            assert instrument, "selected or soloed track has no instrument"

            parameter = get_parameter(
                instrument.device.parameters, device_param_enum, param_position
            )

            parameter.scroll(go_next)

        i = 1
        for param_enum in [
            DeviceParamEnum.DIVA_FILTER_FREQ,
            DeviceParamEnum.DIVA_FILTER_ENV,
            DeviceParamEnum.DIVA_FILTER_RES,
            DeviceParamEnum.DIVA_OUTPUT,
            DeviceParamEnum.DIVA_ENV_ATTACK,
            DeviceParamEnum.DIVA_ENV_DECAY,
            DeviceParamEnum.DIVA_ENV_SUSTAIN,
            DeviceParamEnum.DIVA_ENV_RELEASE,
        ]:
            self.add_encoder(
                identifier=i,
                name=f"encoder {i}",
                on_scroll=partial(scroll_parameter, param_enum, 0),
            )

            i += 1

        for param_enum in [
            DeviceParamEnum.DIVA_ENV_ATTACK,
            DeviceParamEnum.DIVA_ENV_DECAY,
            DeviceParamEnum.DIVA_ENV_SUSTAIN,
            DeviceParamEnum.DIVA_ENV_RELEASE,
        ]:
            self.add_encoder(
                identifier=i,
                name=f"encoder {i}",
                on_scroll=partial(scroll_parameter, param_enum, 1),
            )

            i += 1
