"""
Generate CareScribe's placeholder icon.

A real icon is a design job; this produces something plain and unmistakable so
the build always has one. Run it as the first step of every build — the spec
references the files it writes, so a missing icon would otherwise break the
build rather than just look unfinished.

    python packaging/make_icon.py

Writes ``carescribe.png`` (512x512) and ``carescribe.ico`` (16-256) beside this
file, plus ``carescribe.icns`` when run on macOS. Nothing here fails the build:
a missing font degrades to a bare square rather than raising.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent

SIZE = 512
BACKGROUND = (30, 90, 120, 255)      # a muted clinical teal
FOREGROUND = (255, 255, 255, 255)
CORNER_RADIUS = 96
LETTERS = "CS"

ICO_SIZES = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
ICNS_SIZES = [16, 32, 64, 128, 256, 512]

# Bold faces worth trying, in order, across the platforms this builds on.
FONT_CANDIDATES = (
    "C:/Windows/Fonts/segoeuib.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
    "C:/Windows/Fonts/calibrib.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
)


def _load_font(pixels: int):
    """The first usable bold face, or ``None`` if none of them load."""
    for path in FONT_CANDIDATES:
        if Path(path).is_file():
            try:
                return ImageFont.truetype(path, pixels)
            except Exception:  # noqa: BLE001 — try the next one
                continue
    return None


def render(size: int = SIZE) -> Image.Image:
    """A rounded square with "CS" centred on it."""
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    radius = max(1, int(CORNER_RADIUS * size / SIZE))
    draw.rounded_rectangle([(0, 0), (size - 1, size - 1)], radius, fill=BACKGROUND)

    font = _load_font(int(size * 0.42))
    if font is None:
        # No usable font. A bare square is a worse icon than one with letters on
        # it, and a much better outcome than failing somebody's build.
        print("[make_icon] no TrueType font found — writing a plain square")
        return image

    box = draw.textbbox((0, 0), LETTERS, font=font)
    draw.text(
        ((size - (box[2] - box[0])) / 2 - box[0],
         (size - (box[3] - box[1])) / 2 - box[1]),
        LETTERS,
        font=font,
        fill=FOREGROUND,
    )
    return image


def write_png(image: Image.Image) -> Path:
    path = HERE / "carescribe.png"
    image.save(path, format="PNG")
    return path


def write_ico(image: Image.Image) -> Path:
    path = HERE / "carescribe.ico"
    image.save(path, format="ICO", sizes=ICO_SIZES)
    return path


def write_icns(image: Image.Image) -> Path | None:
    """macOS only. Silently skipped elsewhere — the .app is built on a Mac."""
    if sys.platform != "darwin":
        return None

    path = HERE / "carescribe.icns"

    iconutil = shutil.which("iconutil")
    if iconutil:
        with tempfile.TemporaryDirectory() as workspace:
            iconset = Path(workspace) / "carescribe.iconset"
            iconset.mkdir()
            for edge in ICNS_SIZES:
                image.resize((edge, edge), Image.LANCZOS).save(
                    iconset / f"icon_{edge}x{edge}.png"
                )
                doubled = edge * 2
                image.resize((doubled, doubled), Image.LANCZOS).save(
                    iconset / f"icon_{edge}x{edge}@2x.png"
                )
            try:
                subprocess.run(
                    [iconutil, "-c", "icns", str(iconset), "-o", str(path)],
                    check=True, capture_output=True,
                )
                return path
            except subprocess.CalledProcessError as exc:
                print(f"[make_icon] iconutil failed: {exc.stderr.decode(errors='ignore')}")

    try:
        image.save(path, format="ICNS")
        return path
    except Exception as exc:  # noqa: BLE001
        print(f"[make_icon] could not write .icns: {exc}")
        return None


def main() -> int:
    image = render()
    written = [write_png(image), write_ico(image)]
    icns = write_icns(image)
    if icns:
        written.append(icns)
    elif sys.platform != "darwin":
        print("[make_icon] skipping .icns (not macOS)")

    for path in written:
        print(f"[make_icon] wrote {path.name} ({path.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
