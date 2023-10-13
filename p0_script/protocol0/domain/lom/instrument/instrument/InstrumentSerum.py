from protocol0.domain.lom.device.DeviceEnum import DeviceEnum
from protocol0.domain.lom.instrument.InstrumentColorEnum import InstrumentColorEnum
from protocol0.domain.lom.instrument.InstrumentInterface import InstrumentInterface
from protocol0.domain.lom.instrument.preset.preset_changer.SerumCCPresetChanger import (
    SerumCCPresetChanger,
)
from protocol0.shared.Song import Song


class InstrumentSerum(InstrumentInterface):
    NAME = "Serum"
    DEVICE = DeviceEnum.SERUM
    TRACK_COLOR = InstrumentColorEnum.SERUM
    PRESETS_PATH = (
        "C:\\Users\\thiba\\OneDrive\\Documents\\Xfer\\Serum Presets\\System\\ProgramChanges.txt"
    )
    PRESET_CHANGER = SerumCCPresetChanger

    def on_loaded(self, device_enum: DeviceEnum) -> None:
        track = Song.selected_track()
        track.arm_state.arm()
        self.preset_list.scroll(go_next=True)
        self.preset_list.scroll(go_next=False)
