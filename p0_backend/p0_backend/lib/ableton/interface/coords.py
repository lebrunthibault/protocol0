import enum
from typing import Tuple

from p0_backend.settings import Settings

Coords = Tuple[int, int]
RectCoords = Tuple[int, int, int, int]
settings = Settings()


class CoordsEnum(enum.Enum):
    BROWSER_SEARCH_BOX = (86, 58)
    BROWSER_PLACE_IMPORTED = (50, 308)
