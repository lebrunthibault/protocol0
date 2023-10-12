from protocol0.domain.lom.instrument.InstrumentLoadedEvent import InstrumentLoadedEvent
from protocol0.domain.shared.event.DomainEventBus import DomainEventBus
from protocol0.domain.shared.utils.list import find_if
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger


class InstrumentService(object):
    _DEBUG = True

    def __init__(self) -> None:
        super(InstrumentService, self).__init__()
        DomainEventBus.subscribe(InstrumentLoadedEvent, self._on_instrument_loaded_event)

    def _on_instrument_loaded_event(self, event: InstrumentLoadedEvent) -> None:
        instrument = Song.selected_track().instrument
        if instrument and instrument.device.enum == event.device_enum.instrument_enum:
            instrument.on_loaded(event.device_enum)

    def toggle_macro_control(self, index: int) -> None:
        rack_device = Song.selected_track().instrument_rack_device
        if rack_device is None:
            return

        param = rack_device.parameters[index]
        if param.value == param.min:
            param.value = param.max
        else:
            param.value = param.min

    def scroll_macro_control(self, index: int, go_next: bool, steps: int = 500) -> None:
        rack_device = Song.selected_track().instrument_rack_device
        if rack_device is None:
            return

        param = rack_device.parameters[index]
        if self._DEBUG:
            Logger.info((param.min, param.max, param.value, param.is_quantized))

        param.scroll(go_next, steps=steps)

    def scroll_arp_style(self, go_next: bool) -> None:
        rack_device = Song.selected_track().instrument_rack_device
        if rack_device is None:
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

        for chain in rack_device.chains:
            arp = find_if(lambda d: d.name == "Arpeggiator", chain.devices)
            if not arp:
                continue

            arp_style = find_if(lambda d: d.name == "Style", arp.parameters)
            assert arp_style, f"Could,'t find style parameter on {arp}"

            value_items = [list(arp_style.value_items).index(value) for value in allowed_values]
            arp_style.scroll_slowed(go_next, value_items=value_items)
