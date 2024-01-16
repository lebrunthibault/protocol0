from functools import partial

from protocol0.application.ScriptResetActivatedEvent import ScriptResetActivatedEvent
from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface
from protocol0.domain.lom.device.ClipperService import ClipperService
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.device.ReverbDelayService import (
    scroll_insert_device_volumes,
    scroll_devices_param,
)
from protocol0.domain.lom.device_parameter.DeviceParamEnum import DeviceParamEnum
from protocol0.domain.lom.set.MixingService import MixingService
from protocol0.domain.lom.song.components.TempoComponent import TempoComponent
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus


# noinspection SpellCheckingInspection


class ActionGroupMain(ActionGroupInterface):
    CHANNEL = 4

    def configure(self) -> None:
        # TAP tempo encoder
        self.add_encoder(
            identifier=1,
            name="tap tempo",
            on_press=self._container.get(TempoComponent).tap,
            on_scroll=self._container.get(TempoComponent).scroll,
        )

        # INIT song encoder
        self.add_encoder(
            identifier=4,
            name="(re) initialize the script",
            on_press=partial(DomainEventBus.emit, ScriptResetActivatedEvent()),
        )

        self.add_encoder(
            identifier=5,
            name="Scroll reverb volumes",
            on_scroll=partial(scroll_insert_device_volumes, DeviceEnum.INSERT_REVERB),
        )

        self.add_encoder(
            identifier=6,
            name="Scroll reverb decays",
            on_scroll=partial(
                scroll_devices_param, DeviceEnum.VALHALLA_VINTAGE_VERB, [DeviceParamEnum.DECAY]
            ),
        )

        self.add_encoder(
            identifier=9,
            name="Scroll delay volumes",
            on_scroll=partial(scroll_insert_device_volumes, DeviceEnum.INSERT_DELAY),
        )

        self.add_encoder(
            identifier=10,
            name="Scroll delay feedbacks",
            on_scroll=partial(scroll_devices_param, DeviceEnum.INSERT_DELAY, [DeviceParamEnum.FB]),
        )

        self.add_encoder(
            identifier=12,
            name="all clippers",
            on_press=self._container.get(ClipperService).toggle_all,
            on_scroll=self._container.get(ClipperService).scroll_all,
        )

        self.add_encoder(identifier=13, name="test", on_press=self.action_test)

        # VOLume encoder
        self.add_encoder(
            identifier=16,
            name="volume",
            on_scroll=self._container.get(MixingService).scroll_all_tracks_volume,
        )

    def action_test(self) -> None:
        pass
