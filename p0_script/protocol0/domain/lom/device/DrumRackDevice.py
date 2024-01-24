from typing import List

from protocol0.domain.lom.device.DrumPad import DrumPad
from protocol0.domain.lom.device.RackDevice import RackDevice


class DrumRackDevice(RackDevice):
    @property
    def drum_pads(self) -> List[DrumPad]:
        return [DrumPad(drum_pad) for drum_pad in self._device.drum_pads if drum_pad]

    @property
    def filled_drum_pads(self) -> List[DrumPad]:
        return [drum_pad for drum_pad in self.drum_pads if not drum_pad.is_empty]

    @property
    def selected_drum_pad(self) -> DrumPad:
        return DrumPad(self._device.view.selected_drum_pad)

    @selected_drum_pad.setter
    def selected_drum_pad(self, drum_pad: DrumPad) -> None:
        self._device.view.selected_drum_pad = drum_pad._drum_pad
