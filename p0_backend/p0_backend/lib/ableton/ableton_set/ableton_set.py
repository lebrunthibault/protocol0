import glob
import json
import os.path
import shutil
import time
from json import JSONDecodeError
from os.path import basename, dirname, exists
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel

from p0_backend.lib.ableton.get_set import get_launched_set_path
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
    start_time: float
    end_time: float
    track_names: List[str]


class AbletonSetMetadata(BaseModel):
    path_info: Optional[PathInfo] = None
    scenes: List[SceneStat] = []
    stars: int = 0
    comment: str = ""


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
    def saved_track_names(self) -> List[str]:
        return [basename(t).split(".")[0] for t in self.saved_tracks]

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
    def create(cls, set_filename: str) -> "AbletonSet":
        ableton_set = AbletonSet(path_info=PathInfo.create(set_filename))
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


def set_scene_stats(scene_stats: List[SceneStat]):
    ableton_set = AbletonSet.create(get_launched_set_path())

    ableton_set.metadata.scenes = scene_stats

    ableton_set.save()


class SetPayload(BaseModel):
    name: Optional[str] = None
    stars: Optional[int] = None
    comment: Optional[str] = None


def update_set(filename: str, payload: SetPayload):
    ableton_set = AbletonSet.create(filename)

    if payload.name:
        rename_set(ableton_set, payload.name)
        return

    if payload.stars is not None:
        ableton_set.metadata.stars = payload.stars
    if payload.comment is not None:
        ableton_set.metadata.comment = payload.comment

    ableton_set.save()


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

    if ableton_set.has_own_folder:
        rename(dirname(str(ableton_set.path_info.filename)))


def delete_set(ableton_set: AbletonSet):
    def move_to_trash(filename):
        if not exists(filename):
            return

        dest = filename.replace(
            settings.ableton_set_directory, settings.ableton_set_trash_directory
        )
        shutil.move(filename, dest)

    if ableton_set.has_own_folder:
        move_to_trash(dirname(str(ableton_set.path_info.filename)))
    else:
        move_to_trash(ableton_set.path_info.filename)
        move_to_trash(ableton_set.path_info.metadata_filename)
        move_to_trash(ableton_set.path_info.audio_filename)
        move_to_trash(f"{ableton_set.path_info.audio_filename}.asd")
