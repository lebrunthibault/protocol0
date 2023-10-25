import glob
import os.path
import re
from typing import Optional, List

from loguru import logger

from p0_backend.lib.ableton.ableton import is_ableton_focused
from p0_backend.lib.ableton.ableton_set.ableton_set import (
    AbletonSet,
    AbletonSetPlace,
    AbletonSetCurrentState,
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

    @classmethod
    async def create_from_current_state(cls, current_state: AbletonSetCurrentState) -> None:
        if cls.DEBUG:
            logger.info("registering current state")

        try:
            ableton_set = AbletonSet.create(get_launched_set_path())
        except AssertionError:
            ableton_set = AbletonSet.create(settings.ableton_test_set_path)

        ableton_set.current_state = current_state

        # deduplicate on set title
        existing_set = cls._ACTIVE_SET
        if existing_set is not None:
            if existing_set.path_info.filename != ableton_set.path_info.filename:
                logger.info(f"overwriting active set: {existing_set}")

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


def list_sets(set_place: AbletonSetPlace = None) -> List[AbletonSet]:
    excluded_sets = ["Dancing Feet", "Backup", "test", "tests"]
    ableton_sets = []

    top_folder_path = os.path.join(settings.ableton_set_directory, set_place.folder_name)

    assert os.path.exists(top_folder_path) and os.path.isdir(
        top_folder_path
    ), f"{top_folder_path} does not exist"
    als_files = glob.glob(os.path.join(top_folder_path, "**\\*.als"), recursive=True)

    for als_file in als_files:
        if any(word in als_file for word in excluded_sets):
            continue

        # skip set sub tracks
        if "tracks\\" in als_file.replace(top_folder_path, ""):
            continue

        # skip mastering sets
        if als_file.endswith("master.als"):
            continue

        ableton_sets.append(AbletonSet.create(als_file, set_place))

    return ableton_sets
