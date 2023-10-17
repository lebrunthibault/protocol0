from typing import Optional, List

from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.device.DeviceService import DeviceService
from protocol0.domain.lom.device_parameter.DeviceParameterEnum import DeviceParameterEnum
from protocol0.domain.lom.instrument.InstrumentLoadedEvent import InstrumentLoadedEvent
from protocol0.domain.lom.instrument.instrument.InstrumentParameterEnum import (
    InstrumentParameterEnum,
)
from protocol0.domain.lom.song.components.DeviceComponent import DeviceComponent
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.utils.concurrency import lock
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence


class InstrumentService(object):
    _DEBUG = True

    def __init__(self, device_service: DeviceService, device_component: DeviceComponent) -> None:
        super(InstrumentService, self).__init__()
        self._device_service = device_service
        self._device_component = device_component
        DomainEventBus.subscribe(InstrumentLoadedEvent, self._on_instrument_loaded_event)

    def _on_instrument_loaded_event(self, event: InstrumentLoadedEvent) -> None:
        instrument = Song.selected_track().instrument
        if instrument and instrument.device.enum == event.device_enum.instrument_enum:
            instrument.on_loaded(event.device_enum)

    def scroll_instrument_param(self, name: InstrumentParameterEnum, go_next: bool) -> bool:
        instrument = Song.armed_or_selected_track().instrument

        if instrument and instrument.device and name in instrument.PARAMETER_NAMES:
            self._device_component.select_device(Song.armed_or_selected_track(), instrument.device)
            parameter = instrument.device.get_parameter_by_name(instrument.PARAMETER_NAMES[name])
            parameter.scroll(go_next)
            return True
        elif instrument and instrument.device and callable(getattr(instrument, f"scroll_{name}", None)):
            self._device_component.select_device(Song.armed_or_selected_track(), instrument.device)
            getattr(instrument, f"scroll_{name}")(go_next)
            return True
        else:
            Logger.warning(f"{instrument} cannot scroll {name}")
            return False

    @lock
    def scroll_device_param(
        self,
        device_enum: DeviceEnum,
        param_name: str,
        go_next: bool,
        auto_enable: bool = False,
        value_items: List[int] = None,
    ) -> Optional[Sequence]:
        device = Song.armed_or_selected_track().devices.get_one_from_enum(device_enum)
        if not device:
            Song.armed_or_selected_track().select()
            return self._device_service.load_device(device_enum.name)

        self._device_component.select_device(Song.armed_or_selected_track(), device)
        device.is_enabled = True
        param = device.get_parameter_by_name(param_name)

        if param is None:
            Logger.warning(f"Couldn't find {param_name} on {device}")
            return None

        if value_items:
            param.scroll_slowed(go_next, value_items=value_items)
        else:
            param.scroll(go_next)

        # disable the device the the param reaches its minimum
        if auto_enable:
            if (param.value == param.min and device.is_enabled) or (
                param.value != param.min and not device.is_enabled
            ):
                device.toggle()

        return None

    @lock
    def toggle_device(self, device_enum: DeviceEnum) -> Optional[Sequence]:
        device = Song.armed_or_selected_track().devices.get_one_from_enum(device_enum)

        if not device:
            Song.armed_or_selected_track().select()
            return self._device_service.load_device(device_enum.name)

        device.toggle()
        return None

    def scroll_volume(self, go_next: bool) -> None:
        scrolled = self.scroll_instrument_param(InstrumentParameterEnum.VOLUME, go_next)

        if not scrolled:
            Song.armed_or_selected_track().scroll_volume(go_next)

    def scroll_low_pass_filter(self, go_next: bool) -> Optional[Sequence]:
        scrolled = self.scroll_instrument_param(InstrumentParameterEnum.FILTER, go_next)

        if not scrolled:
            return self.scroll_device_param(
                DeviceEnum.EQ_EIGHT, DeviceParameterEnum.EQ_EIGHT_FREQUENCY_8_A.parameter_name, go_next
            )

        return None

    def scroll_reverb(self, go_next: bool) -> None:
        if self.scroll_instrument_param(InstrumentParameterEnum.REVERB, go_next):
            return

        reverb = Song.armed_or_selected_track().devices.get_one_from_enum(DeviceEnum.INSERT_REVERB)
        if reverb:
            self._device_component.select_device(Song.armed_or_selected_track(), reverb)
            reverb.get_parameter_by_name(DeviceParameterEnum.WET).scroll(go_next)
        else:
            sends = Song.armed_or_selected_track().devices.mixer_device.sends
            if len(sends):
                sends[-1].scroll(go_next)

    @lock
    def scroll_delay(self, go_next: bool) -> Optional[Sequence]:
        if self.scroll_instrument_param(InstrumentParameterEnum.DELAY, go_next):
            return None
        else:
            return self.scroll_device_param(
                DeviceEnum.INSERT_DELAY, DeviceParameterEnum.WET.parameter_name, go_next
            )

    @lock
    def scroll_arp_style(self, go_next: bool) -> Optional[Sequence]:
        value_items = [
            0,  # "Up",
            1,  # "Down",
            # 2, "UpDown",
            # 3, "DownUp",
            # 4, "Up & Down",
            # 5, "Down & Up",
            6,  # "Converge",
            # 7, "Diverge",
            # 8, "Con & Diverge",
            9,  # "Pinky Up",
            # 10, "Pinky UpDown",
            11,  # "Thumb Up",
            # 12, "Thumb UpDown",
            # 13, "Play Order",
            14,  # "Chord Trigger",
            # 15, "Random",
            # 16, "Random Other",
            # 17, "Random Once",
        ]
        return self.scroll_device_param(DeviceEnum.ARPEGGIATOR, "Style", go_next, value_items=value_items)
