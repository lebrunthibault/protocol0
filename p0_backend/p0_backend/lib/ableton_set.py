import glob
import os.path
import re
import time
from os.path import basename, dirname
from typing import List, Optional

from loguru import logger
from protocol0.application.command.EmitBackendEventCommand import (
    EmitBackendEventCommand,
)
from protocol0.application.command.ShowMessageCommand import ShowMessageCommand
from pydantic import BaseModel

from p0_backend.api.client.p0_script_api_client import p0_script_client
from p0_backend.settings import Settings
from p0_backend.celery.celery import notification_window
from p0_backend.lib.ableton.ableton import is_ableton_focused
from p0_backend.lib.ableton.get_set import (
    get_ableton_windows,
    get_set_from_title,
)
from p0_backend.lib.enum.notification_enum import NotificationEnum
from p0_backend.lib.errors.Protocol0Error import Protocol0Error
from p0_backend.lib.timer import start_timer
from p0_backend.lib.window.window import get_focused_window_title

settings = Settings()


class AbletonTrack(BaseModel):
    name: str
    type: str
    index: int


class AbletonSet(BaseModel):
    def __repr__(self):
        return f"AbletonSet('{self.title}')"

    def __str__(self):
        return self.__repr__()

    id: str
    path: Optional[str]  # computed only by the backend
    title: Optional[str]  # computed only by the backend
    muted: bool
    current_track: AbletonTrack
    selected_track: AbletonTrack
    track_count: int
    drum_rack_visible: bool

    @property
    def is_untitled(self):
        return self.title is None or self.title == "None"

    @property
    def tracks_folder(self):
        assert self.path is not None, "current set is Untitled"
        return f"{dirname(self.path)}\\tracks"

    @classmethod
    def all_tracks_folder(cls) -> List[str]:
        return next(os.walk(f"{settings.ableton_set_directory}\\tracks"))[1]

    @property
    def temp_track_folder(self) -> str:
        return f"{settings.ableton_set_directory}\\tracks"

    @property
    def saved_temp_track(self) -> Optional[str]:
        return next(iter(glob.glob(f"{self.temp_track_folder}\\*.als")), None)

    @property
    def saved_tracks(self) -> List[str]:
        return glob.glob(f"{self.tracks_folder}\\*.als")

    @property
    def saved_track_names(self) -> List[str]:
        return [basename(t).split(".")[0] for t in self.saved_tracks]

    @property
    def is_current_track_saved(self) -> bool:
        saved_track = self.saved_temp_track
        if saved_track is None:
            return False

        saved_track_name = basename(saved_track).replace(".als", "")

        assert saved_track_name == self.current_track.name, "track saved mismatch"
        assert time.time() - os.path.getmtime(saved_track) <= 2, "track not saved recently"

        return True


class AbletonSetManager:
    DEBUG = True
    LAST_SET_OPENED_AT: Optional[float] = None
    _ACTIVE_SET: Optional[AbletonSet] = None

    @classmethod
    async def register(cls, ableton_set: AbletonSet):
        if cls.DEBUG:
            logger.info(f"registering set {ableton_set}")

        launched_sets = get_ableton_windows()
        set_title = re.match(r"([^*]*)", launched_sets[0]).group(1).strip()
        assert set_title, "set title is empty"

        if ableton_set.is_untitled:
            if set_title.startswith("Untitled"):
                ableton_set.path = settings.ableton_test_set_path
                ableton_set.title = "Test"
            elif set_title.startswith("Default"):
                ableton_set.path = (
                    f"{settings.ableton_set_directory}\\Default.als"
                )
                ableton_set.title = "Default"
            else:
                ableton_set.title = set_title
                ableton_set.path = get_set_from_title(set_title)

        if cls.LAST_SET_OPENED_AT is not None:
            startup_duration = time.time() - cls.LAST_SET_OPENED_AT
            logger.info(f"took {startup_duration:.2f}")
            command = ShowMessageCommand(f"Startup took {startup_duration:.2f}s")
            start_timer(1, lambda: p0_script_client().dispatch(command))

            cls.LAST_SET_OPENED_AT = None

        # deduplicate on set title
        existing_set = cls._ACTIVE_SET
        if existing_set is not None:
            if existing_set.title != ableton_set.title:
                logger.warning(f"Cannot overwrite active set: {existing_set}")
                return

            _check_track_name_change(existing_set, ableton_set)

        cls._ACTIVE_SET = ableton_set

        from p0_backend.api.http_server.ws import ws_manager

        await ws_manager.broadcast_server_state()

        # update backend
        time.sleep(0.5)  # fix too fast backend ..?
        command = EmitBackendEventCommand("set_updated", data=ableton_set.dict())
        command.set_id = ableton_set.id
        p0_script_client().dispatch(command, log=False)

    @classmethod
    async def remove(cls, set_id: str):
        if cls._ACTIVE_SET is None:
            logger.warning(f"Cannot remove set id '{set_id}', no active set")
        elif cls._ACTIVE_SET.id != set_id:
            logger.warning(f"Cannot remove set id '{set_id}', active set is {cls._ACTIVE_SET}")
        else:
            cls._ACTIVE_SET = None

    @classmethod
    def update_set(cls, title: str, path: Optional[str] = None):
        ableton_set = cls.active()

        ableton_set.title = title
        if path is None:
            path = f"{settings.ableton_set_directory}\\tracks\\{title}\\{title}.als"

        ableton_set.path = path

        command = EmitBackendEventCommand("set_updated", data=ableton_set.dict())
        command.set_id = ableton_set.id
        p0_script_client().dispatch(command, log=False)

    @classmethod
    def active(cls) -> Optional[AbletonSet]:
        if cls._ACTIVE_SET is None:
            raise Protocol0Error("no active set")

        return cls._ACTIVE_SET

    @classmethod
    def has_active_set(cls) -> bool:
        return cls._ACTIVE_SET is not None


def _check_track_name_change(existing_set: AbletonSet, new_set: AbletonSet):
    if (
        existing_set.track_count == new_set.track_count
        and existing_set.current_track.index == new_set.current_track.index
        and existing_set.current_track.name != new_set.current_track.name
        and existing_set.current_track.type == "SimpleAudioTrack"
        and existing_set.current_track.name in existing_set.saved_track_names
    ):
        notification_window.delay("You updated a saved track", NotificationEnum.WARNING.value, True)
        show_saved_tracks()


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
        and AbletonSetManager.active().title == set_title
    ):
        return AbletonSetManager.active()

    return None


def show_saved_tracks():
    os.startfile(AbletonSetManager.active().tracks_folder)


def delete_saved_track(track_name: str):
    active_set = AbletonSetManager.active()
    assert track_name in active_set.saved_track_names

    track_path = f"{active_set.tracks_folder}\\{track_name}.als"

    os.unlink(track_path)
