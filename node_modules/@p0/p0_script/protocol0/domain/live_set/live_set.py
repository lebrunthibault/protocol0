from protocol0.domain.lom.SessionRing import get_session_ring_scene_offset
from protocol0.domain.live_set.LiveSet import LiveTrack


def launch_kick() -> None:
    track = LiveTrack.KICK.get()
    cs_index = get_session_ring_scene_offset() % 8
    from protocol0.shared.logging.Logger import Logger

    Logger.dev((track, cs_index))
    track.clip_slots[cs_index].fire()


def launch_fx() -> None:
    track = LiveTrack.FX.get()
    cs_index = get_session_ring_scene_offset() % 8
    from protocol0.shared.logging.Logger import Logger

    Logger.dev((track, cs_index))
    track.clip_slots[cs_index].fire()


def launch_drop() -> None:
    launch_kick()
    launch_fx()
