import glob
import json
import os.path
import shutil
from enum import Enum
from json import JSONDecodeError
from os.path import basename, dirname, exists, join, isabs
from pathlib import Path
from typing import List, Optional

from loguru import logger
from pydantic import BaseModel, Field

from backend.settings import Settings, SETS_DIRECTORY

settings = Settings()


class PathInfo(BaseModel):
    filename: str = Field(exclude=True)
    relative_name: str
    name: str
    saved_at: Optional[float] = 0

    @property
    def tracks_folder(self):
        assert self.filename is not None, "current set is Untitled"
        return f"{dirname(self.filename)}/tracks"

    @property
    def metadata_filename(self) -> str:
        return self.filename.replace(".als", ".json")

    @property
    def audio_filename(self) -> str:
        return self.filename.replace(".als", ".wav")

    @property
    def mp3_filename(self) -> str:
        return self.filename.replace(".als", ".mp3")

    @classmethod
    def create(cls, filename: str) -> "PathInfo":
        assert not isabs(filename), f"Got an absolute filename: {filename}"
        path = Path(join(SETS_DIRECTORY, filename))

        return cls(
            filename=str(path),
            relative_name=filename,
            name=path.stem,
            saved_at=path.stat().st_mtime,
        )


class SceneStat(BaseModel):
    name: str
    start: int
    end: int
    track_names: List[str]


class AbletonSetStage(str, Enum):
    DRAFT = "DRAFT"
    BETA = "BETA"
    RELEASE = "RELEASE"


class AbletonSetPlace(Enum):
    TRACKS = "TRACKS"
    ARCHIVE = "ARCHIVE"
    RELEASED = "RELEASED"
    TRASH = "TRASH"

    @property
    def folder_name(self) -> str:
        return {
            self.TRACKS: "tracks",
            self.ARCHIVE: "other/archive",
            self.RELEASED: "other/released",
            self.TRASH: "other/trash",
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
    stars: int = 0
    comment: str = ""
    stage: AbletonSetStage = AbletonSetStage.DRAFT


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

    @property
    def has_own_folder(self) -> bool:
        return (
            basename(dirname(str(self.path_info.filename))).lower().strip()
            == self.path_info.name.lower().strip()
        )

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
                        path_info=PathInfo.create(
                            ableton_set.path_info.metadata_filename.removeprefix(
                                SETS_DIRECTORY + "/"
                            )
                        ),
                    )
                except JSONDecodeError as e:
                    from loguru import logger

                    logger.error(e)
                    pass

        # handle audio info
        if os.path.exists(ableton_set.path_info.audio_filename):
            audio_path = os.path.relpath(ableton_set.path_info.audio_filename, SETS_DIRECTORY)
            audio_url = f"http://localhost:{settings.port}/static/{audio_path}"

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


class SetPayload(BaseModel):
    name: Optional[str] = None
    stars: Optional[int] = None
    comment: Optional[str] = None
    stage: Optional[AbletonSetStage] = None


def update_set(filename: str, payload: SetPayload):
    ableton_set = AbletonSet.create(filename)

    if payload.stars is not None:
        ableton_set.metadata.stars = payload.stars
    if payload.comment is not None:
        ableton_set.metadata.comment = payload.comment
    if payload.stage is not None:
        ableton_set.metadata.stage = payload.stage

    ableton_set.save()

    if payload.name and payload.name != ableton_set.path_info.name:
        rename_set(ableton_set, payload.name)


def rename_set(ableton_set: AbletonSet, name: str):
    def rename(filename: str) -> None:
        if not exists(filename):
            return

        directory, base_name = os.path.split(filename)
        new_name = os.path.join(directory, name)

        if Path(base_name).suffix:
            new_name += f".{'.'.join(base_name.split('.')[1:])}"

        os.rename(filename, new_name)

    assert ableton_set.path_info.filename

    rename(ableton_set.path_info.filename)
    rename(ableton_set.path_info.metadata_filename)
    rename(ableton_set.path_info.audio_filename)
    rename(f"{ableton_set.path_info.audio_filename}.asd")
    rename(ableton_set.path_info.mp3_filename)
    rename(f"{ableton_set.path_info.mp3_filename}.asd")

    if ableton_set.has_own_folder:
        rename(dirname(str(ableton_set.path_info.filename)))


def list_sets(set_place: AbletonSetPlace = None) -> List[AbletonSet]:
    excluded_sets = ["Backup", "test", "tests"]
    ableton_sets = []

    top_folder_path = os.path.join(SETS_DIRECTORY, set_place.folder_name)
    from loguru import logger

    logger.success(top_folder_path)

    assert os.path.exists(top_folder_path) and os.path.isdir(
        top_folder_path
    ), f"{top_folder_path} does not exist"
    als_files = glob.glob(os.path.join(top_folder_path, "**/*.als"), recursive=True)
    from loguru import logger

    logger.success(als_files)

    for als_file in als_files:
        if any(word in als_file for word in excluded_sets):
            continue

        # skip set sub tracks
        if "tracks/" in als_file.replace(top_folder_path, ""):
            continue

        # skip mastering sets
        if als_file.endswith("master.als"):
            continue

        ableton_sets.append(
            AbletonSet.create(als_file.removeprefix(SETS_DIRECTORY + "/"), set_place)
        )

    return ableton_sets


def move_set(path: str, set_place: AbletonSetPlace):
    ableton_set = AbletonSet.create(path)
    if not ableton_set:
        return

    def move_file(filename):
        if not exists(filename):
            return

        dest = filename.replace(ableton_set.place.folder_name, set_place.folder_name)
        shutil.move(filename, dest)

    if ableton_set.has_own_folder:
        move_file(dirname(str(ableton_set.path_info.filename)))
    else:
        move_file(ableton_set.path_info.filename)
        move_file(ableton_set.path_info.metadata_filename)
        move_file(ableton_set.path_info.audio_filename)
        move_file(f"{ableton_set.path_info.audio_filename}.asd")
        move_file(f"{ableton_set.path_info.mp3_filename}")
        move_file(f"{ableton_set.path_info.mp3_filename}.mp3.asd")
