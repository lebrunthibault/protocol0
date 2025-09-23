from _Framework.ControlSurface import ControlSurface, get_control_surfaces
from protocol0.domain.shared.utils.list import find_if


def get_session_ring_scene_offset() -> int:
    from Launchpad import Launchpad

    launchpad = find_if(lambda s: type(s) == Launchpad, get_control_surfaces())
    return launchpad._highlighting_session_component._scene_offset
