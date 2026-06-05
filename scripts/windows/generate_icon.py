"""Generates the Protocol0 Windows icon (installer/assets/protocol0.ico).

Faithful to the site's badge (src/website/favicon.svg): rounded dark-gradient square,
thin border, bold blue "P" centered. We draw the badge with Pillow rather than rasterize
the SVG, to avoid any system binary dependency (cairosvg/inkscape) on the CI side: Pillow
installs everywhere as a pure wheel.

Output: a multi-resolution .ico (16/32/48/64/128/256) committed at installer/assets/
protocol0.ico and embedded by the Rust agent's build.rs (PE resource of the exe + shortcuts)
and loaded by the systray (src/agent/src/tray.rs via include_bytes!).

This is a MANUAL maintenance tool, NOT a build step: the committed .ico is the source of truth
for the build (build_agent_exe.ps1 does not run this). Re-run it only when the source badge
src/website/favicon.svg changes, then commit the regenerated installer/assets/protocol0.ico.

Usage: python scripts/windows/generate_icon.py   (Pillow required: pip install Pillow)
"""
from __future__ import annotations

import os
import sys

from PIL import Image, ImageDraw, ImageFont

# Colors taken from src/website/favicon.svg.
BG_TOP = (27, 29, 34, 255)        # #1b1d22 (top-left corner of the gradient)
BG_BOTTOM = (10, 11, 13, 255)     # #0a0b0d (bottom-right)
BORDER = (255, 255, 255, 38)      # rgba(255,255,255,0.15)
P_BLUE = (77, 159, 255, 255)      # #4d9fff

# We render at a large size (supersampling) then downscale to each icon size:
# clean antialiasing of the rounded corners and the glyph.
RENDER = 1024

ICON_SIZES = [16, 32, 48, 64, 128, 256]

# Bold font candidates, in order of preference. On the Windows build runner (where this
# script actually runs), Segoe UI / Arial Bold are guaranteed present.
FONT_CANDIDATES = [
    r"C:\Windows\Fonts\seguisb.ttf",   # Segoe UI Semibold
    r"C:\Windows\Fonts\segoeuib.ttf",  # Segoe UI Bold
    r"C:\Windows\Fonts\arialbd.ttf",   # Arial Bold
    "DejaVuSans-Bold.ttf",             # shipped with Pillow (Linux/CI fallback)
    "Arial Bold.ttf",
]


def _diagonal_gradient(size: int) -> Image.Image:
    """Linear gradient BG_TOP -> BG_BOTTOM along the (0,0)->(1,1) diagonal,
    like the SVG's linearGradient."""
    base = Image.new("RGBA", (size, size))
    px = base.load()
    max_d = (size - 1) * 2 or 1
    for y in range(size):
        for x in range(size):
            t = (x + y) / max_d  # 0 at top-left, 1 at bottom-right
            r = round(BG_TOP[0] + (BG_BOTTOM[0] - BG_TOP[0]) * t)
            g = round(BG_TOP[1] + (BG_BOTTOM[1] - BG_TOP[1]) * t)
            b = round(BG_TOP[2] + (BG_BOTTOM[2] - BG_TOP[2]) * t)
            px[x, y] = (r, g, b, 255)
    return base


def _load_font(px_size: int) -> ImageFont.FreeTypeFont:
    for path in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(path, px_size)
        except OSError:
            continue
    # Last resort: the default bitmap font (ignores px_size, but avoids a crash if no
    # TTF can be found).
    return ImageFont.load_default()


def _render_badge(size: int) -> Image.Image:
    """Draws the full badge at resolution `size`."""
    # SVG geometry (viewBox 32) scaled: rect x=1 y=1 w=30 h=30 rx=8.
    s = size / 32.0
    inset = round(1 * s)
    radius = round(8 * s)
    rect = [inset, inset, size - inset - 1, size - inset - 1]

    # Rounded mask.
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle(rect, radius=radius, fill=255)

    # Gradient background applied through the mask.
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    img.paste(_diagonal_gradient(size), (0, 0), mask)

    draw = ImageDraw.Draw(img)
    # Subtle border.
    draw.rounded_rectangle(rect, radius=radius, outline=BORDER, width=max(1, round(s)))

    # Letter "P": font-size 20 in a viewBox 32 -> ~0.625 * size.
    font = _load_font(round(20 * s))
    # Optical centering: center the glyph bbox on the badge center.
    bbox = draw.textbbox((0, 0), "P", font=font)
    gw = bbox[2] - bbox[0]
    gh = bbox[3] - bbox[1]
    tx = (size - gw) / 2 - bbox[0]
    ty = (size - gh) / 2 - bbox[1]
    draw.text((tx, ty), "P", font=font, fill=P_BLUE)
    return img


def main() -> int:
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    out_dir = os.path.join(repo_root, "installer", "assets")
    os.makedirs(out_dir, exist_ok=True)
    out_ico = os.path.join(out_dir, "protocol0.ico")

    master = _render_badge(RENDER)
    # Render each size from the high-res master (crisp downscale), rather than letting
    # Pillow re-shrink from a single frame. The largest is the base image, the others are
    # stacked via append_images: without this Pillow writes only one resolution to the .ico.
    frames = [master.resize((n, n), Image.LANCZOS) for n in ICON_SIZES]
    largest = frames[-1]
    largest.save(
        out_ico,
        format="ICO",
        sizes=[(n, n) for n in ICON_SIZES],
        append_images=frames[:-1],
    )

    # Companion 256 PNG (handy for the site / visual debugging).
    out_png = os.path.join(out_dir, "protocol0.png")
    master.resize((256, 256), Image.LANCZOS).save(out_png, format="PNG")

    print(f"OK -> {out_ico}")
    print(f"OK -> {out_png}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
