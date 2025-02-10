from typing import List, cast

import Live
from _Framework.SubjectSlot import SlotManager

from protocol0.domain.lom.device.DeviceChain import DeviceChain
from protocol0.domain.lom.device.Sample.Sample import Sample
from protocol0.domain.lom.device.SimplerDevice import SimplerDevice
from protocol0.domain.shared.utils.string import smart_string


class DrumPad(SlotManager):
    def __init__(self, drum_pad: Live.DrumPad.DrumPad) -> None:
        super(DrumPad, self).__init__()
        self._drum_pad = drum_pad
        self.chains: List[DeviceChain] = []
        # self._chains_listener.subject = self._drum_pad
        # self._chains_listener()

    def __repr__(self) -> str:
        out = "DrumPad(name='%s', note=%s" % (self.name, self.note)
        if self.is_empty:
            out += ", empty=True"
        return out + ")"

    # @subject_slot("chains")
    # def _chains_listener(self) -> None:
    #     self.chains = [
    #         DeviceChain(chain, index) for index, chain in enumerate(self._drum_pad.chains)
    #     ]

    @property
    def name(self) -> str:
        return smart_string(self._drum_pad.name)

    @property
    def sample(self) -> Sample:
        assert not self.is_empty, "pad is empty"
        simpler = cast(SimplerDevice, self.chains[0].devices[0])
        assert isinstance(simpler, SimplerDevice), "pad device is not a simpler"

        return simpler.sample

    @property
    def note(self) -> int:
        return self._drum_pad.note

    @property
    def is_empty(self) -> bool:
        return len(self._drum_pad.chains) == 0
