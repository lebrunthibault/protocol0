import re
from typing import Optional

from loguru import logger

from p0_backend.lib.ableton.ableton import is_ableton_focused
from p0_backend.lib.ableton.ableton_set.ableton_set import (
    AbletonSet,
    AbletonSetCurrentState,
    AbletonTrack,
    AbletonSetTracks,
    PathInfo,
)
from p0_backend.lib.ableton.get_set import (
    get_launched_set_path,
)
from p0_backend.lib.errors.Protocol0Error import Protocol0Error
from p0_backend.lib.window.window import get_focused_window_title
from p0_backend.settings import Settings

settings = Settings()


class AbletonSetManager:
    DEBUG = True
    _ACTIVE_SET: Optional[AbletonSet] = None
    _ACTIVE_SET_TRACKS: Optional[AbletonSetTracks] = None

    @classmethod
    async def create_from_current_state(cls, current_state: AbletonSetCurrentState) -> None:
        if cls.DEBUG:
            logger.info("registering current state")

        path_info = PathInfo.create(get_launched_set_path())

        ableton_set = cls._ACTIVE_SET
        if not ableton_set or ableton_set.path_info.filename != path_info.filename:
            try:
                ableton_set = AbletonSet.create(get_launched_set_path())
            except AssertionError:
                try:
                    ableton_set = AbletonSet.create(settings.ableton_test_set_path)
                except AssertionError as e:
                    logger.error(e)
                    return

        ableton_set.update_current_state(current_state)

        cls._ACTIVE_SET = ableton_set

    @classmethod
    async def remove(cls, filename: str):
        if cls._ACTIVE_SET is None:
            logger.warning(f"Cannot remove set '{filename}', no active set")
        elif cls._ACTIVE_SET.path_info.filename != filename:
            logger.warning(f"Cannot remove set '{filename}', active set is {cls._ACTIVE_SET}")
        else:
            cls._ACTIVE_SET = None

    @classmethod
    def active(cls) -> AbletonSet:
        if cls._ACTIVE_SET is None:
            raise Protocol0Error("no active set")

        return cls._ACTIVE_SET

    @classmethod
    def has_active_set(cls) -> bool:
        return cls._ACTIVE_SET is not None

    @classmethod
    def clear_state(cls) -> None:
        cls.active().tracks.clear_selection_history()

    @classmethod
    def update_track_color(cls, track: AbletonTrack, new_color: int) -> None:
        cls.active().tracks.update_track_color(track, new_color)


def get_focused_set() -> Optional[AbletonSet]:
    if not is_ableton_focused():
        return None

    title = get_focused_window_title()

    match = re.match("([^[*]*)\*?\s*(\[[^[]*])? - Ableton Live.*", title)

    if match is None:
        return None

    set_title = match.group(1).strip()

    if (
        AbletonSetManager.has_active_set()
        and AbletonSetManager.active().path_info.name == set_title
    ):
        return AbletonSetManager.active()

    return None
