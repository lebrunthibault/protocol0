from _Framework.ControlSurface import ControlSurface, get_control_surfaces
from protocol0.domain.shared.utils.list import find_if


def get_session_ring_scene_offset() -> int:
    from Launchpad_Pro_MK3_mod.launchpad_pro_mk3_mod import Launchpad_Pro_MK3_Mod

    launchpad = find_if(lambda s: type(s) == Launchpad_Pro_MK3_Mod, get_control_surfaces())
    return launchpad._session_ring.scene_offset
