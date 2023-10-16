from functools import partial

from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface
from protocol0.domain.lom.clip.MidiClip import MidiClip
from protocol0.domain.lom.instrument.instrument.InstrumentService import InstrumentService
from protocol0.domain.lom.set.MixingService import MixingService
from protocol0.shared.Song import Song


class ActionGroupRack(ActionGroupInterface):
    CHANNEL = 2

    def configure(self) -> None:
        # RACK macro control encoders
        instrument_service = self._container.get(InstrumentService)

        self.add_encoder(
            identifier=1,
            name="scroll filter",
            on_scroll=instrument_service.scroll_low_pass_filter,
        )
        self.add_encoder(
            identifier=2,
            name="scroll attack",
            on_scroll=partial(instrument_service.scroll_param, "attack"),
        )
        self.add_encoder(
            identifier=3,
            name="scroll release",
            on_scroll=partial(instrument_service.scroll_param, "release"),
        )
        self.add_encoder(
            identifier=4,
            name="scroll volume",
            on_scroll=instrument_service.scroll_volume,
        )
        self.add_encoder(
            identifier=5,
            name="scroll track high pass filter",
            on_press=instrument_service.toggle_eq,
            on_scroll=instrument_service.scroll_high_pass_filter,
        )
        self.add_encoder(
            identifier=6,
            name="scroll 8va bassa",
            on_press=instrument_service.toggle_octava_bassa,
            on_scroll=instrument_service.scroll_octava_bassa,
        )
        self.add_encoder(
            identifier=7,
            name="scroll reverb",
            on_scroll=instrument_service.scroll_reverb,
        )
        self.add_encoder(
            identifier=8,
            name="scroll delay",
            on_scroll=instrument_service.scroll_delay,
        )
        self.add_encoder(
            identifier=9,
            name="scroll arp mode",
            on_press=instrument_service.toggle_arp,
            on_scroll=instrument_service.scroll_arp_style,
        )
        self.add_encoder(
            identifier=10,
            name="scroll arp rate",
            on_scroll=instrument_service.scroll_arp_rate,
        )
        self.add_encoder(
            identifier=11,
            name="scroll arp gate",
            on_scroll=instrument_service.scroll_arp_gate,
        )
        self.add_encoder(
            identifier=12,
            name="scroll lfo tool",
            on_scroll=instrument_service.scroll_lfo_tool,
        )

        # -----

        # VELO encoder
        self.add_encoder(
            identifier=15,
            name="smooth selected clip velocities",
            on_scroll=lambda: Song.selected_clip(MidiClip).scale_velocities,
        )
        # VOLume encoder
        self.add_encoder(
            identifier=16,
            name="volume",
            on_scroll=self._container.get(MixingService).scroll_all_tracks_volume,
        )
