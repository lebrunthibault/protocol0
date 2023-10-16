from functools import partial
from typing import Optional

from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.device.DeviceService import DeviceService
from protocol0.domain.lom.device_parameter.DeviceParameterEnum import DeviceParameterEnum
from protocol0.domain.lom.instrument.InstrumentLoadedEvent import InstrumentLoadedEvent
from protocol0.domain.lom.instrument.instrument.InstrumentParameterEnum import \
    InstrumentParameterEnum
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.utils.concurrency import lock
from protocol0.domain.shared.utils.list import find_if
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger
from protocol0.shared.sequence.Sequence import Sequence


class InstrumentService(object):
    _DEBUG = True

    def __init__(self, device_service: DeviceService) -> None:
        super(InstrumentService, self).__init__()
        self._device_service = device_service
        DomainEventBus.subscribe(InstrumentLoadedEvent, self._on_instrument_loaded_event)

    def _on_instrument_loaded_event(self, event: InstrumentLoadedEvent) -> None:
        instrument = Song.selected_track().instrument
        if instrument and instrument.device.enum == event.device_enum.instrument_enum:
            instrument.on_loaded(event.device_enum)

    def toggle_macro_control(self, index: int) -> None:
        rack_device = Song.armed_or_selected_track().instrument_rack_device
        if rack_device:
            rack_device.parameters[index].toggle()

    def scroll_macro_control(self, index: int, go_next: bool, steps: int = 500) -> None:
        rack_device = Song.armed_or_selected_track().instrument_rack_device
        if rack_device is None:
            return

        param = rack_device.parameters[index]
        if self._DEBUG:
            Logger.info((param.min, param.max, param.value, param.is_quantized))

        param.scroll(go_next, steps=steps)

    def scroll_param(self, name: InstrumentParameterEnum, go_next: bool) -> bool:
        instrument = Song.armed_or_selected_track().instrument

        if instrument and name in instrument.PARAMETER_NAMES:
            parameter = instrument.device.get_parameter_by_name(instrument.PARAMETER_NAMES[name])
            parameter.scroll(go_next)
            return True
        elif instrument and callable(getattr(instrument, f"scroll_{name}", None)):
            getattr(instrument, f"scroll_{name}")(go_next)
            return True
        else:
            Logger.warning(f"{instrument} cannot scroll {name}")
            return False

    def scroll_volume(self, go_next: bool) -> None:
        scrolled = self.scroll_param(InstrumentParameterEnum.VOLUME, go_next)

        if not scrolled:
            Song.armed_or_selected_track().scroll_volume(go_next)

    @lock
    def scroll_low_pass_filter(self, go_next: bool) -> Optional[Sequence]:
        scrolled = self.scroll_param(InstrumentParameterEnum.FILTER, go_next)

        if not scrolled:
            return self._scroll_eq_parameter(DeviceParameterEnum.EQ_EIGHT_FREQUENCY_8_A, go_next)

        return None

    def toggle_eq(self) -> None:
        eq_eight = Song.armed_or_selected_track().devices.get_one_from_enum(DeviceEnum.EQ_EIGHT)
        if eq_eight:
            eq_eight.is_enabled = not eq_eight.is_enabled

    @lock
    def scroll_high_pass_filter(self, go_next: bool) -> Sequence:
        return self._scroll_eq_parameter(DeviceParameterEnum.EQ_EIGHT_FREQUENCY_1_A, go_next)

    def _scroll_eq_parameter(self, param: DeviceParameterEnum, go_next: bool) -> Sequence:
        eq_eight = Song.armed_or_selected_track().devices.get_one_from_enum(DeviceEnum.EQ_EIGHT)

        seq = Sequence()

        if not eq_eight:
            Song.armed_or_selected_track().select()

            seq.add(partial(self._device_service.load_device, DeviceEnum.EQ_EIGHT.name))
        else:
            eq_eight.is_enabled = True
            frequency = eq_eight.get_parameter_by_name(param)
            frequency.scroll(go_next)

        return seq.done()

    def toggle_octava_bassa(self, go_next: bool) -> None:
        octava = Song.armed_or_selected_track().devices.get_one_from_name("Octava")
        if octava is None:
            Logger.warning("Cannot find Octava device")
            return

        octava.toggle()

    def scroll_octava_bassa(self, go_next: bool) -> None:
        octava = Song.armed_or_selected_track().devices.get_one_from_name("Octava")
        if octava is None:
            Logger.warning("Cannot find Octava device")
            return

        velocity = octava.get_parameter_by_name("Vel")
        velocity.scroll(go_next)

        if velocity == 0 and not octava.is_enabled or velocity != 0 and not octava.is_enabled:
            octava.toggle()

    def scroll_reverb(self, go_next: bool) -> None:
        if self.scroll_param(InstrumentParameterEnum.REVERB, go_next):
            return

        insert_reverb = Song.armed_or_selected_track().devices.get_one_from_enum(
            DeviceEnum.INSERT_REVERB
        )
        if insert_reverb:
            insert_reverb.parameters[1].scroll(go_next)
        else:
            sends = Song.armed_or_selected_track().devices.mixer_device.sends
            if len(sends):
                sends[-1].scroll(go_next)

    def scroll_delay(self, go_next: bool) -> None:
        if self.scroll_param(InstrumentParameterEnum.DELAY, go_next):
            return

        insert_delay = Song.armed_or_selected_track().devices.get_one_from_enum(
            DeviceEnum.INSERT_DELAY
        )
        if insert_delay:
            insert_delay.parameters[1].scroll(go_next)

    def toggle_arp(self) -> None:
        arp = Song.armed_or_selected_track().devices.get_one_from_enum(DeviceEnum.ARPEGGIATOR)
        if arp is None:
            Logger.warning("Cannot find arp device")
            return

        arp.get_parameter_by_name("Device On").toggle()

    def scroll_arp_style(self, go_next: bool) -> None:
        arp = Song.armed_or_selected_track().devices.get_one_from_enum(DeviceEnum.ARPEGGIATOR)
        if arp is None:
            Logger.warning("Cannot find arp device")
            return

        allowed_values = [
            "Up",
            "Down",
            # "UpDown",
            # "DownUp",
            # "Up & Down",
            # "Down & Up",
            "Converge",
            # "Diverge",
            # "Con & Diverge",
            "Pinky Up",
            # "Pinky UpDown",
            "Thumb Up",
            # "Thumb UpDown",
            # "Play Order",
            "Chord Trigger",
            # "Random",
            # "Random Other",
            # "Random Once",
        ]

        arp_style = arp.get_parameter_by_name("Style")
        value_items = [list(arp_style.value_items).index(value) for value in allowed_values]
        arp_style.scroll_slowed(go_next, value_items=value_items)

    def scroll_arp_rate(self, go_next: bool):
        arp = Song.armed_or_selected_track().devices.get_one_from_enum(DeviceEnum.ARPEGGIATOR)
        if arp is None:
            Logger.warning("Cannot find arp device")
            return

        arp.get_parameter_by_name("Rate").scroll(go_next, steps=200)

    def scroll_arp_gate(self, go_next: bool):
        arp = Song.armed_or_selected_track().devices.get_one_from_enum(DeviceEnum.ARPEGGIATOR)
        if arp is None:
            Logger.warning("Cannot find arp device")
            return

        arp.get_parameter_by_name("Gate").scroll(go_next)

    @lock
    def scroll_lfo_tool(self, go_next: bool) -> Sequence:
        lfo_tool: Optional[Device] = find_if(
            lambda d: d.enum == DeviceEnum.LFO_TOOL, Song.armed_or_selected_track().devices
        )

        seq = Sequence()

        if not lfo_tool:
            Song.armed_or_selected_track().select()

            seq.add(partial(self._device_service.load_device, DeviceEnum.LFO_TOOL.name))
        else:
            seq.add(partial(lfo_tool.parameters[1].scroll, go_next))

        return seq.done()