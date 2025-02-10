import colorsys
from dataclasses import dataclass, field
from time import sleep
from typing import List, Optional, Tuple, Iterator

from PIL import ImageGrab
from loguru import logger

from p0_backend.lib.ableton.interface.coords import Coords, RectCoords
from p0_backend.lib.ableton.interface.pixel_color_enum import PixelColorEnum, RGBColor
from p0_backend.lib.decorators import timeit
from p0_backend.lib.errors.Protocol0Error import Protocol0Error
from p0_backend.lib.mouse.mouse import move_to
from p0_backend.settings import Settings

settings = Settings()
_DEBUG = False


@dataclass
class PixelBox:
    pixels: List[Tuple[int, Tuple]] = field(repr=False)
    bbox: RectCoords
    from_right: bool
    from_bottom: bool

    def __post_init__(self):
        self.x1, self.y1, self.x2, self.y2 = self.bbox

        self.width = self.x2 - self.x1
        self.height = self.y2 - self.y1

        if _DEBUG:
            from loguru import logger

            logger.info(self)
            logger.info(f"w: {self.width}, height: {self.height}, pixel_count: {self.pixel_count}")

    @property
    def pixel_count(self):
        return self.width * self.height

    def iterate_pixels(self) -> Iterator:
        pixels = self.pixels
        if self.from_bottom:
            pixels = list(reversed(self.pixels))

        return iter(pixels[::10])

    def iterate_line(self, i, backwards=False):
        current_y = i // self.width
        line_end = (current_y + 1) * self.width

        line = self.pixels[i:line_end]
        if backwards:
            line_end = current_y * self.width
            line = list(reversed(self.pixels[line_end:i]))

        yield from line

    def get_coords(self, i: int):
        rel_width = i % self.width
        rel_height = i // self.width

        if _DEBUG:
            logger.info(f"i: {i}")
            logger.info(f"rel_width: {rel_width}")
            logger.info(f"rel_height: {rel_height}")

        return (rel_width) + self.x1, (rel_height) + self.y1


@timeit
def get_coords_for_color(
    colors: List[PixelColorEnum],
    bbox: RectCoords,
    from_right=False,
    from_bottom=False,
    min_width: Optional[int] = None,
) -> Coords:
    screen = ImageGrab.grab(bbox=bbox)
    pixels = list(enumerate(screen.getdata()))

    pixel_box = PixelBox(pixels, bbox, from_right, from_bottom)
    colors_rgb = [c.rgb for c in colors]

    pixel_list = pixel_box.iterate_pixels()

    for i, color in pixel_list:
        if color not in colors_rgb:
            continue

        # get the left or right boundary
        for j, color in pixel_box.iterate_line(i, backwards=not from_right):
            if color not in colors_rgb:
                break
            i = j

        if min_width is not None:
            pixel_line = list(pixel_box.iterate_line(i, backwards=pixel_box.from_bottom))
            if len(pixel_line) < min_width or pixel_line[min_width][1] not in colors_rgb:
                # not wide enough, consume the pixels
                for k, _ in pixel_list:
                    if abs(k - i) // pixel_box.width >= 20:
                        break

        return pixel_box.get_coords(i)

    raise Protocol0Error(f"colors not found in screen: {colors}")


def get_pixel_color_at(coords: Coords) -> Optional[PixelColorEnum]:
    image = ImageGrab.grab()
    rgb_color = image.getpixel(coords)

    for color_enum in PixelColorEnum:
        if color_enum.rgb == rgb_color:
            return color_enum

    logger.warning(f"didn't find color enum from rgb {rgb_color} at {coords}")

    return None


def is_rgb_color_black(rgb_color: RGBColor) -> bool:
    hsv_color = colorsys.rgb_to_hsv(*rgb_color)

    return hsv_color[2] <= 20 or rgb_color == (121, 121, 121)


def get_pixel_having_color(
    coords_list: List[Coords], color_enum: PixelColorEnum = None, is_black=False, debug=False
) -> Optional[Coords]:
    image = ImageGrab.grab()
    assert color_enum is not None or is_black

    for coords in coords_list:
        if debug:
            move_to(coords)
            logger.info(coords)
            sleep(1)

        rgb_color = image.getpixel(coords)
        if color_enum is not None and rgb_color == color_enum.rgb:
            return coords
        elif is_black and is_rgb_color_black(rgb_color):
            return coords

    return None
