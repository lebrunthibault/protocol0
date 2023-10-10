from protocol0.domain.shared.utils.list import find_if
from protocol0.shared.Song import Song
from protocol0.shared.logging.Logger import Logger


class InstrumentService(object):
    _DEBUG = True

    def toggle_macro_control(self, index: int) -> None:
        rack_device = Song.selected_track().instrument_rack_device
        assert rack_device is not None, "No instrument rack device"

        param = rack_device.parameters[index]
        from protocol0.shared.logging.Logger import Logger
        Logger.dev(("toggle", rack_device, param))
        if param.value == param.min:
            param.value = param.max
        else:
            param.value = param.min

    def scroll_macro_control(self, index: int, go_next: bool, steps: int = 1000) -> None:
        rack_device = Song.selected_track().instrument_rack_device
        assert rack_device is not None, "No instrument rack device"

        param = rack_device.parameters[index]
        if self._DEBUG:
            Logger.info((param.min, param.max, param.value, param.is_quantized))

        param.scroll(go_next, steps=steps)

    def scroll_arp_style(self, go_next: bool) -> None:
        rack_device = Song.selected_track().instrument_rack_device
        assert rack_device is not None, "No instrument rack device"

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
