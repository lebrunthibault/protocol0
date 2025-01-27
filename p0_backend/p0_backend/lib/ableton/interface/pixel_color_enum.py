from enum import Enum
from typing import Tuple

from p0_backend.settings import Settings

RGBColor = Tuple[int, int, int]

settings = Settings()


class PixelColorEnum(Enum):
    """used when doing pixel color detection"""

    BUTTON_ACTIVATED_YELLOW = "FFB532"

    ELEMENT_FOCUSED = "FF39D4"
    ELEMENT_SELECTED = "BFE9FF"

    CONTEXT_MENU_BACKGROUND = "DCDCDC"

    @classmethod
    def context_menu_background(cls):
        return cls.CONTEXT_MENU_BACKGROUND

    EXPLORER_SELECTED_ENTRY = "CCE8FF"
    EXPLORER_SELECTED_ENTRY_LIGHT = "E5F3FF"

    # needed for closest color detection
    SEPARATOR = "4B4B4B"
    LEFT_SIZE = "6E6E6E"

    @classmethod
    def hex_to_rgb(cls, color: str) -> RGBColor:
        return int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)

    @property
    def rgb(self) -> RGBColor:
        return PixelColorEnum.hex_to_rgb(self.value)
