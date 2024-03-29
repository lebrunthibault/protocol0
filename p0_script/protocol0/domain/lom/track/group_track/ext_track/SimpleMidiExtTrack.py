from typing import Any, Optional, List

from protocol0.domain.lom.device.Device import Device
from protocol0.domain.lom.track.simple_track.midi.SimpleMidiTrack import SimpleMidiTrack
from protocol0.domain.shared.utils.list import find_if


def get_external_device(devices: List[Device]) -> Optional[Device]:
    return find_if(lambda d: d.enum is not None and d.enum.is_external_device, list(devices))


class SimpleMidiExtTrack(SimpleMidiTrack):
    """Tagging class for the main midi track of an ExternalSynthTrack"""

    def __init__(self, *a: Any, **k: Any) -> None:
        super(SimpleMidiExtTrack, self).__init__(*a, **k)
        self.clip_tail.active = False

    @property
    def external_device(self) -> Optional[Device]:
        return get_external_device(list(self.devices))
