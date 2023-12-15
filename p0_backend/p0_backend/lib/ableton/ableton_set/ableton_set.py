import glob
import json
import os.path
import time
from enum import Enum
from json import JSONDecodeError
from os.path import basename, dirname
from pathlib import Path
from typing import List, Optional

from loguru import logger
from pydantic import BaseModel

from p0_backend.lib.ableton.get_set import get_launched_set_path
from p0_backend.lib.notification import notify
from p0_backend.settings import Settings

settings = Settings()


class PathInfo(BaseModel):
    filename: str
    name: str
    saved_at: Optional[float] = 0

    @property
    def tracks_folder(self):
        assert self.filename is not None, "current set is Untitled"
        return f"{dirname(self.filename)}\\tracks"

    @property
    def metadata_filename(self) -> str:
        return self.filename.replace(".als", ".json")

    @property
    def audio_filename(self) -> str:
        return self.filename.replace(".als", ".wav")

    @classmethod
    def create(cls, filename: str) -> "PathInfo":
        path = Path(filename)

        return cls(filename=filename, name=path.stem, saved_at=path.stat().st_mtime)


class SceneStat(BaseModel):
    name: str
    start: int
    end: int
    track_names: List[str]


class AbletonSetPlace(Enum):
    TRACKS = "TRACKS"
    ARCHIVE = "ARCHIVE"
    RELEASED = "RELEASED"
    TRASH = "TRASH"

    @property
    def folder_name(self) -> str:
        return {
            self.TRACKS: "tracks",
            self.ARCHIVE: "other\\archive",
            self.RELEASED: "other\\released",
            self.TRASH: "other\\trash",
        }[
            self  # type: ignore[index]
        ]

    @classmethod
    def from_directory(cls, directory: str) -> Optional["AbletonSetPlace"]:
        parent_dir = dirname(directory)
        for place in AbletonSetPlace:
            if directory.endswith(place.folder_name) or parent_dir.endswith(place.folder_name):
                return place

        logger.warning(f"Cannot find AbletonSetPlace for {directory}")

        return None


class AbletonSetMetadata(BaseModel):
    path_info: Optional[PathInfo] = None
    tempo: float = 0
    scenes: List[SceneStat] = []


class AudioInfo(BaseModel):
    url: str
    outdated: bool


class AbletonTrack(BaseModel):
    name: str
    index: int


class SceneTrackState(BaseModel):
    track_name: str
    group_name: str
    has_clip: bool
    is_playing: bool
    is_armed: bool


class AbletonScene(BaseModel):
    drums: List[SceneTrackState]
    harmony: List[SceneTrackState]
    melody: List[SceneTrackState]
    bass: List[SceneTrackState]


class AbletonSetCurrentState(BaseModel):
    selected_scene: AbletonScene
    current_track: AbletonTrack
    selected_track: AbletonTrack
    drum_rack_visible: bool


class AbletonSet(BaseModel):
    def __repr__(self):
        return f"AbletonSet('{self.path_info.name if self.path_info else ''}')"

    def __str__(self):
        return self.__repr__()

    place: Optional[AbletonSetPlace]
    path_info: Optional[PathInfo] = None
    audio: Optional[AudioInfo] = None
    metadata: Optional[AbletonSetMetadata] = None
    current_state: Optional[AbletonSetCurrentState] = None

    @classmethod
    def all_tracks_folder(cls) -> List[str]:
        return next(os.walk(f"{settings.ableton_set_directory}\\tracks"))[1]

    @property
    def saved_temp_track(self) -> Optional[str]:
        temp_track_folder = f"{settings.ableton_set_directory}\\tracks"
        return next(iter(glob.glob(f"{temp_track_folder}\\*.als")), None)

    @property
    def saved_tracks(self) -> List[str]:
        return glob.glob(f"{self.path_info.tracks_folder}\\*.als")

    @property
    def is_current_track_saved(self) -> bool:
        saved_track = self.saved_temp_track
        if saved_track is None:
            return False

        saved_track_name = basename(saved_track).replace(".als", "")

        assert saved_track_name == self.current_state.current_track.name, "track saved mismatch"
        assert time.time() - os.path.getmtime(saved_track) <= 2, "track not saved recently"

        return True

    @classmethod
    def create(cls, set_filename: str, set_place: AbletonSetPlace = None) -> "AbletonSet":
        ableton_set = AbletonSet(
            place=set_place or AbletonSetPlace.from_directory(dirname(set_filename)),
            path_info=PathInfo.create(set_filename),
        )
        ableton_set.metadata = AbletonSetMetadata()

        # restore from file
        if os.path.exists(ableton_set.path_info.metadata_filename):
            with open(ableton_set.path_info.metadata_filename, "r") as f:
                try:
                    data = json.load(f)
                    ableton_set.metadata = AbletonSetMetadata(
                        **data,
                        path_info=PathInfo.create(ableton_set.path_info.metadata_filename),
                    )
                except JSONDecodeError as e:
                    from loguru import logger

                    logger.error(e)
                    pass

        # handle audio info
        if os.path.exists(ableton_set.path_info.audio_filename):
            audio_url = f"http://localhost:8000/static/{os.path.relpath(ableton_set.path_info.audio_filename, settings.ableton_set_directory)}"

            audio_saved_at = os.path.getmtime(ableton_set.path_info.audio_filename)
            assert ableton_set.path_info.saved_at, "saved_at not computed"
            ableton_set.audio = AudioInfo(
                url=audio_url,
                outdated=ableton_set.path_info.saved_at - audio_saved_at > 30 * 60,  # 30 min
            )

        return ableton_set

    def save(self):
        with open(self.path_info.metadata_filename, "w") as f:
            f.write(self.metadata.model_dump_json(exclude={"path_info"}))


def set_scene_stats(tempo: float, l2_disabled: float, scene_stats: List[SceneStat]):
    ableton_set = AbletonSet.create(get_launched_set_path())

    ableton_set.metadata.tempo = tempo
    ableton_set.metadata.scenes = scene_stats

    song_bar_length = round(scene_stats[-1].end / 4)
    message = f"{song_bar_length} bars"
    if l2_disabled:
        message += "\nEnabling L2"
    notify(message)

    ableton_set.save()
