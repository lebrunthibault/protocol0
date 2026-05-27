from pydantic import BaseModel
from typing import List


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
