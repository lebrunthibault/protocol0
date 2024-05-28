import re
from typing import Optional, List

from loguru import logger

from p0_backend.lib.ableton.ableton import is_ableton_focused
from p0_backend.lib.ableton.ableton_set.ableton_set import (
    AbletonSet,
    AbletonSetCurrentState,
    AbletonTrack,
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
    SELECTED_TRACKS_HISTORY: List[AbletonTrack] = []

    @classmethod
    async def create_from_current_state(cls, current_state: AbletonSetCurrentState) -> None:
        if cls.DEBUG:
            logger.info("registering current state")

        try:
            ableton_set = AbletonSet.create(get_launched_set_path())
        except AssertionError:
            try:
                ableton_set = AbletonSet.create(settings.ableton_test_set_path)
            except AssertionError as e:
                logger.error(e)
                return

        ableton_set.current_state = current_state
        logger.success(current_state.tracks)

        # deduplicate on set title
        existing_set = cls._ACTIVE_SET
        if existing_set:
            logger.success((existing_set, existing_set.current_state.tracks))
            if existing_set.path_info.filename != ableton_set.path_info.filename:
                logger.info(f"overwriting active set: {existing_set}")

            if existing_set.current_state.tracks and not current_state.tracks:
                logger.success("replacing tracks !")
                ableton_set.current_state.tracks = current_state.tracks

            if existing_set.current_state == ableton_set.current_state:
                logger.info("No change")
                return

        cls._ACTIVE_SET = ableton_set

        from p0_backend.api.http_server.ws import ws_manager

        if (
            existing_set
            and existing_set.current_state.selected_scene
            != ableton_set.current_state.selected_scene
        ):
            await ws_manager.broadcast_active_set()

        # keep a selected track history
        logger.success(cls.SELECTED_TRACKS_HISTORY)
        logger.success(current_state.selected_track)
        if current_state.selected_track in cls.SELECTED_TRACKS_HISTORY:
            cls.SELECTED_TRACKS_HISTORY.remove(current_state.selected_track)

        cls.SELECTED_TRACKS_HISTORY.insert(0, current_state.selected_track)

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
        cls.SELECTED_TRACKS_HISTORY = []

    @classmethod
    def update_track_color(cls, track_name: str, previous_color: int, new_color: int) -> None:
        track = next(
            filter(
                lambda t: AbletonTrack(name=track_name, color=previous_color) == t,  # noqa
                cls.SELECTED_TRACKS_HISTORY,
            )
        )
        track.color = new_color

    @classmethod
    def delete_track(cls, track: AbletonTrack) -> None:
        if track in cls.SELECTED_TRACKS_HISTORY:
            cls.SELECTED_TRACKS_HISTORY.remove(track)


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
