import json
import os.path
import subprocess
from enum import Enum
from json import JSONDecodeError
from os.path import dirname, isabs
from pathlib import Path
from typing import List, Optional

from loguru import logger
from pydantic import BaseModel

from p0_backend.lib.ableton.get_set import get_launched_set_path
from p0_backend.lib.explorer import open_explorer
from p0_backend.lib.notification import notify
from p0_backend.settings import Settings

settings = Settings()


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


class PathInfo(BaseModel):
    filename: str
    name: str
    saved_at: Optional[float] = 0
    place: AbletonSetPlace

    @property
    def metadata_filename(self) -> str:
        return self.filename.replace(".als", ".json")

    @property
    def audio_filename(self) -> str:
        return self.filename.replace(".als", ".wav")

    @classmethod
    def create(cls, filename: str) -> "PathInfo":
        if not isabs(filename):
            filename = f"{settings.ableton_set_directory}\\{filename}"

        assert os.path.exists(filename), f"fichier introuvable : {filename}"

        path = Path(filename)

        return cls(
            filename=filename,
            name=path.stem,
            saved_at=path.stat().st_mtime,
            place=AbletonSetPlace.from_directory(dirname(filename)) or AbletonSetPlace.TRACKS,
        )


class SceneStat(BaseModel):
    name: str
    start: int
    end: int
    track_names: List[str]


class AbletonSetMetadata(BaseModel):
    path_info: Optional[PathInfo] = None
    tempo: float = 0
    scenes: List[SceneStat] = []


class AudioInfo(BaseModel):
    url: str
    outdated: bool


class AbletonTrack(BaseModel):
    name: str
    color: int

    @property
    def rgb_color(self) -> str:
        return {
            2: "#CC9927",
            13: "#FFFFFF",
            20: "#00BFAF",
            23: "#007DC0",
            45: "#BFBA69",
            61: "#539F31",
            69: "#3C3C3C",
        }.get(self.color, "#FFFFFF")


class AbletonSetCurrentState(BaseModel):
    selected_track: AbletonTrack
    tracks: List[AbletonTrack]


class AbletonSetTracks:
    def __init__(self, tracks: List[AbletonTrack]):
        self._tracks = tracks
        self._selection_history: List[AbletonTrack] = []

    def __repr__(self):
        return f"AbletonSetTracks('{len(self.all)}')"

    def __bool__(self) -> bool:
        return len(self.all) > 0

    @property
    def all(self) -> List[AbletonTrack]:
        return self._tracks

    @property
    def selection_history(self) -> List[AbletonTrack]:
        return self._selection_history

    def get(self, f: AbletonTrack) -> Optional[AbletonTrack]:
        return next(
            filter(
                lambda t: f == t,  # noqa
                self.all,
            ),
            None,  # type: ignore[arg-type]
        )

    def update(self, tracks: List[AbletonTrack]):
        self._tracks = tracks
        self._selection_history = [t for t in self._selection_history if t in tracks]

    def flag_selected(self, track: AbletonTrack) -> None:
        if track.name.lower() == "master":
            return None

        handled_track = self.get(track)

        if not handled_track:
            return None

        if handled_track in self.selection_history:
            self.selection_history.remove(handled_track)

        self.selection_history.insert(0, handled_track)

    def clear_selection_history(self) -> None:
        self._selection_history = []

    def update_track_color(self, track: AbletonTrack, color: int) -> None:
        handled_track = self.get(track)

        if not handled_track:
            return None

        handled_track.color = color


class AbletonSet:
    def __init__(
        self, path_info: PathInfo, metadata: AbletonSetMetadata, audio: Optional[AudioInfo]
    ):
        self.path_info = path_info
        self.metadata = metadata
        self.audio = audio

        self.current_state: Optional[AbletonSetCurrentState] = None
        self.tracks: Optional[AbletonSetTracks] = AbletonSetTracks([])

    def __repr__(self):
        return f"AbletonSet('{self.path_info.name if self.path_info else ''}')"

    def __str__(self):
        return self.__repr__()

    @classmethod
    def create(cls, set_filename: str) -> "AbletonSet":
        path_info = PathInfo.create(set_filename)
        metadata = AbletonSetMetadata()
        audio_info = None

        # restore from file
        if os.path.exists(path_info.metadata_filename):
            with open(path_info.metadata_filename, "r") as f:
                try:
                    data = json.load(f)
                    metadata = AbletonSetMetadata(
                        **data,
                        path_info=PathInfo.create(path_info.metadata_filename),
                    )
                except JSONDecodeError as e:
                    from loguru import logger

                    logger.error(e)
                    pass

        # handle audio info
        if os.path.exists(path_info.audio_filename):
            audio_url = f"http://localhost:8000/static/{os.path.relpath(path_info.audio_filename, settings.ableton_set_directory)}"

            audio_saved_at = os.path.getmtime(path_info.audio_filename)
            assert path_info.saved_at, "saved_at not computed"
            audio_info = AudioInfo(
                url=audio_url,
                outdated=path_info.saved_at - audio_saved_at > 30 * 60,  # 30 min
            )

        return AbletonSet(path_info=path_info, metadata=metadata, audio=audio_info)

    def update_current_state(self, current_state: AbletonSetCurrentState):
        if not self.current_state:
            self.current_state = current_state
        else:
            self.current_state.selected_track = current_state.selected_track

        if current_state.tracks:
            self.tracks.update(current_state.tracks)

        assert current_state.selected_track, f"selected track is None in {current_state}"

        self.tracks.flag_selected(current_state.selected_track)

    def save(self):
        with open(self.path_info.metadata_filename, "w") as f:
            f.write(self.metadata.model_dump_json(exclude={"path_info"}))


def set_scene_stats(tempo: float, scene_stats: List[SceneStat]):
    ableton_set = AbletonSet.create(get_launched_set_path())

    ableton_set.metadata.tempo = tempo

    if scene_stats:
        ableton_set.metadata.scenes = scene_stats

        song_bar_length = round(scene_stats[-1].end / 4)
        notify(f"{song_bar_length} bars")

    ableton_set.save()


def prepare_for_soundcloud(path: str):
    path_info = PathInfo.create(path)
    assert path_info.audio_filename, "Track has not wav file"
    audio_output = path_info.audio_filename.replace(".wav", "-streaming.wav")
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            path_info.audio_filename,
            "-af",
            "adelay=500|500",
            audio_output,
        ]
    )
    open_explorer(audio_output)
