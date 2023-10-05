from functools import partial

from protocol0.application.control_surface.ActionGroupInterface import ActionGroupInterface
from protocol0.domain.lom.clip.MidiClip import MidiClip
from protocol0.domain.lom.device.DeviceService import DeviceService
from protocol0.domain.lom.instrument.instrument.InstrumentService import InstrumentService
from protocol0.domain.lom.set.MixingService import MixingService
from protocol0.shared.Song import Song


class ActionGroupRack(ActionGroupInterface):
    CHANNEL = 2

    def configure(self) -> None:
        # RACK macro control encoders
        instrument_service = self._container.get(InstrumentService)

        for i in range(1, 13):
            if i == 5:
                self.add_encoder(
                    identifier=5,
                    name="edit track high pass filter",
                    on_press=self._container.get(DeviceService).scroll_high_pass_filter,
                )
                continue

            self.add_encoder(
                identifier=i,
                name=f"edit macro control {i}",
                on_press=partial(instrument_service.toggle_macro_control, i),
                on_scroll=partial(instrument_service.scroll_macro_control, i),
            )

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
