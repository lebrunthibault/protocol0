import enum
from typing import Tuple

from p0_backend.api.settings import Settings

Coords = Tuple[int, int]
RectCoords = Tuple[int, int, int, int]
settings = Settings()


class CoordsEnum(enum.Enum):
    @classmethod
    def browser_left_size(cls) -> Coords:
        return (30, 165) if settings.is_ableton_11 else (30, 221)

    # @classmethod
    # def browser_left_size_2(cls) -> Coords:
    #     return (30, 190) if settings.is_ableton_11 else cls.browser_left_size()

    @classmethod
    def browser_place_tracks(cls) -> Coords:
        return (97, 286) if settings.is_ableton_11 else (97, 310)

    BROWSER_PLACE_TRACKS_2 = (97, 308)  # when 'All results' is shown

    BROWSER_ALL_RESULTS = (49, 163)
    BROWSER_SEARCH_BOX = (86, 58)
    BROWSER_PLACE_IMPORTED = (50, 308)
    BROWSER_FREE_TRACK_SPOT = (310, 284)

    # Relative coordinates
    REV2_ACTIVATION_MIDDLE_BUTTON = (784, 504)
    REV2_PROGRAM = (1067, 147)
