import glob
import json
import os.path
import time
from os.path import basename, dirname
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel

from p0_backend.lib.ableton.get_set import get_launched_set_path
from p0_backend.settings import Settings

settings = Settings()


class AbletonSetPath(BaseModel):
    filename: Optional[str]
    name: Optional[str]
    saved_at: Optional[float]

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
    def create(cls, filename: str) -> "AbletonSetPath":
        path = Path(filename)

        return cls(filename=filename, name=path.stem, saved_at=path.stat().st_mtime)


class MetadataFileInfo(BaseModel):
    filename: str
    saved_at: float


class SceneStat(BaseModel):
    name: str
    start_time: float
    end_time: float
    track_names: List[str]


class AbletonSetMetadata(BaseModel):
    path_info: Optional[MetadataFileInfo]
    scenes: List[SceneStat] = []
    stars: int = 0


class AudioFileInfo(BaseModel):
    filename: str
    url: str
    saved_at: float
    outdated: bool


class AbletonTrack(BaseModel):
    name: str
    type: str
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
    track_count: int
    drum_rack_visible: bool


class AbletonSet(BaseModel):
    def __repr__(self):
        return f"AbletonSet('{self.path_info.name}')"

    def __str__(self):
        return self.__repr__()

    path_info: AbletonSetPath
    audio_info: Optional[AudioFileInfo]
    metadata: Optional[AbletonSetMetadata]
    current_state: Optional[AbletonSetCurrentState]

    @property
    def is_untitled(self):
        return self.path_info.filename is None or Path(self.path_info.filename).stem == "None"

    @property
    def has_own_folder(self) -> bool:
        return basename(dirname(str(self.path_info.filename))).lower().strip() == self.path_info.name

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
        set_path = AbletonSetPath.create(set_filename)

        # handle metadata
        if os.path.exists(set_path.metadata_filename):
            with open(set_path.metadata_filename, "r") as f:
                ableton_set = AbletonSet(**json.load(f))
                ableton_set.path_info = set_path

                metadata_path = AbletonSetPath(
                    filename=set_path.metadata_filename,
                    saved_at=os.path.getmtime(set_path.metadata_filename),
                )
                ableton_set.metadata = ableton_set.metadata or AbletonSetMetadata(
                    path_info=metadata_path
                )
                ableton_set.metadata.path_info = metadata_path
        else:
            ableton_set = AbletonSet(path_info=set_path)
            ableton_set.metadata = AbletonSetMetadata()

        # handle audio info
        if os.path.exists(ableton_set.path_info.audio_filename):
            audio_url = f"http://localhost:8000/static/{os.path.relpath(ableton_set.path_info.audio_filename, settings.ableton_set_directory)}"

            audio_saved_at = os.path.getmtime(ableton_set.path_info.audio_filename)
            assert ableton_set.path_info.saved_at, "saved_at not computed"
            ableton_set.audio_info = AudioFileInfo(
                filename=ableton_set.path_info.audio_filename,
                saved_at=audio_saved_at,
                url=audio_url,
                outdated=ableton_set.path_info.saved_at - audio_saved_at > 30 * 60,  # 30 min
            )

        return ableton_set

    def save(self):
        with open(self.path_info.metadata_filename, "w") as f:
            f.write(self.json())


def set_scene_stats(scene_stats: List[SceneStat]):
    ableton_set = AbletonSet.create(get_launched_set_path())

    ableton_set.metadata.scenes = scene_stats
    ableton_set.save()


def set_stars(filename: str, stars: int):
    ableton_set = AbletonSet.create(filename)

    ableton_set.metadata.stars = stars
    ableton_set.save()
