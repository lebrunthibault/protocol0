from typing import List

from pydantic import BaseModel


class SceneStat(BaseModel):
    name: str
    start_time: float
    end_time: float
    track_names: List[str]


class SceneStats(BaseModel):
    filename: str
    saved_at: float
    scenes: List[SceneStat]
