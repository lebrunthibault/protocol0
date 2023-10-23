import glob
import os.path
import re
import time
from itertools import chain
from os.path import basename, dirname
from pathlib import Path
from typing import Optional, Dict, List

from loguru import logger

from p0_backend.api.client.p0_script_api_client import p0_script_client
from p0_backend.lib.ableton.ableton import is_ableton_focused
from p0_backend.lib.ableton.ableton_set.ableton_set import AbletonSet, PathInfo
from p0_backend.lib.ableton.get_set import (
    get_launched_set_path,
)
from p0_backend.lib.errors.Protocol0Error import Protocol0Error
from p0_backend.lib.window.window import get_focused_window_title
from p0_backend.settings import Settings
from protocol0.application.command.EmitBackendEventCommand import (
    EmitBackendEventCommand,
)

settings = Settings()


class AbletonSetManager:
    DEBUG = True
    _ACTIVE_SET: Optional[AbletonSet] = None

    @classmethod
    async def register(cls, ableton_set: AbletonSet) -> None:
        if cls.DEBUG:
            logger.info(f"registering set {ableton_set}")

        try:
            ableton_set.path_info = PathInfo.create(get_launched_set_path())
        except AssertionError:
            ableton_set.path_info = PathInfo.create(settings.ableton_test_set_path)

        # deduplicate on set title
        existing_set = cls._ACTIVE_SET
        if existing_set is not None:
            if existing_set.path_info.filename != ableton_set.path_info.filename:
                logger.info(f"overwriting active set: {existing_set}")

        if existing_set == ableton_set:
            logger.info("No change")
            return

        cls._ACTIVE_SET = ableton_set

        from p0_backend.api.http_server.ws import ws_manager

        if (
            existing_set
            and existing_set.current_state.selected_scene
            != ableton_set.current_state.selected_scene
        ):
            await ws_manager.broadcast_server_state()

        # update backend
        time.sleep(0.5)  # fix too fast backend ..?
        command = EmitBackendEventCommand("set_updated", data=ableton_set.path_info.model_dump())
        command.set_id = ableton_set.path_info.filename
        p0_script_client().dispatch(command, log=False)

    @classmethod
    async def remove(cls, filename: str):
        if cls._ACTIVE_SET is None:
            logger.warning(f"Cannot remove set '{filename}', no active set")
        elif cls._ACTIVE_SET.path_info.filename != filename:
            logger.warning(f"Cannot remove set '{filename}', active set is {cls._ACTIVE_SET}")
        else:
            cls._ACTIVE_SET = None

    @classmethod
    def active(cls) -> Optional[AbletonSet]:
        if cls._ACTIVE_SET is None:
            raise Protocol0Error("no active set")

        return cls._ACTIVE_SET

    @classmethod
    def has_active_set(cls) -> bool:
        return cls._ACTIVE_SET is not None


def _get_focused_set_title() -> Optional[str]:
    if not is_ableton_focused():
        return None

    title = get_focused_window_title()

    match = re.match("([^[*]*)\*?\s*(\[[^[]*])? - Ableton Live.*", title)

    if match is None:
        return None

    return match.group(1).strip()


def get_focused_set() -> Optional[AbletonSet]:
    set_title = _get_focused_set_title()

    if (
        set_title is not None
        and AbletonSetManager.has_active_set()
        and AbletonSetManager.active().path_info.name == set_title
    ):
        return AbletonSetManager.active()

    return None


def list_sets(archive=False) -> Dict[str, List[AbletonSet]]:
    if archive:
        top_folders = ["_released", "paused"]
    else:
        top_folders = ["drafts", "tracks"]

    excluded_sets = ["Dancing Feet", "Backup"]
    ableton_sets = {}

    for top_folder in top_folders:
        top_folder_path = os.path.join(settings.ableton_set_directory, top_folder)
        ableton_sets[top_folder] = []

        assert os.path.exists(top_folder_path) and os.path.isdir(
            top_folder_path
        ), f"{top_folder} does not exist"
        als_files = glob.glob(os.path.join(top_folder_path, "**\\*.als"), recursive=True)

        for als_file in als_files:
            if any(word in als_file for word in excluded_sets):
                continue

            if top_folder not in ("drafts",) and Path(als_file).stem != basename(dirname(als_file)):
                continue

            ableton_sets[top_folder].append(AbletonSet.create(als_file))

    return ableton_sets


def get_set(path: str) -> Optional[AbletonSet]:
    path = path.replace("\\\\", "\\")

    ableton_sets = list(chain.from_iterable(list_sets().values()))

    return next(s for s in ableton_sets if s.path_info.filename == path)


def delete_saved_track(track_name: str):
    active_set = AbletonSetManager.active()
    assert track_name in active_set.saved_track_names

    track_path = f"{active_set.path_info.tracks_folder}\\{track_name}.als"

    os.unlink(track_path)
