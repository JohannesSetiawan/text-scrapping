"""Sprite set creation: fit, mirror, tile and stack character sprites."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from PIL import Image

SPRITE_SIZE = 160
ICON_SIZE = 64
ICON_COPIES = 2
SHEET_COPIES = 4
SIDE_FACINGS = ("left", "right")

_ROLE_SUFFIXES = {"front": "f", "back": "b", "side": "s"}
_TRANSPARENT = (0, 0, 0, 0)


class SpriteCreatorError(Exception):
    """Raised when a sprite set cannot be built."""


@dataclass(frozen=True)
class SpritePackage:
    """Generated sprite images for a single character number."""

    number: int
    side_facing: str
    front_sprite: Image.Image
    back_sprite: Image.Image
    icons: Image.Image
    spritesheet: Image.Image


def resolve_sprite_number(names: Mapping[str, str]) -> int:
    """Extract the shared sprite number from the uploaded filenames.

    Args:
        names: Mapping of role ("front", "back", "side") to filename

    Returns:
        The common sprite number

    Raises:
        SpriteCreatorError: If a filename is malformed or the numbers differ
    """
    numbers = {role: _parse_sprite_number(name, role) for role, name in names.items()}

    if len(set(numbers.values())) != 1:
        detail = ", ".join(f"{role}={number}" for role, number in numbers.items())
        raise SpriteCreatorError(
            f"All three sprites must share the same number, got {detail}."
        )

    return next(iter(numbers.values()))


def load_sprite_image(image_bytes: bytes, role: str) -> Image.Image:
    """Decode an uploaded sprite into RGBA mode.

    Args:
        image_bytes: Raw PNG bytes
        role: Role of the sprite, used for error messages

    Returns:
        RGBA PIL Image

    Raises:
        SpriteCreatorError: If the bytes cannot be decoded as an image
    """
    try:
        return Image.open(BytesIO(image_bytes)).convert("RGBA")
    except Exception as exc:
        raise SpriteCreatorError(f"Could not read the {role} sprite: {exc}") from exc


def build_sprite_package(
    *,
    number: int,
    side_facing: str,
    front: Image.Image,
    back: Image.Image,
    side: Image.Image,
) -> SpritePackage:
    """Build every sprite output from the three source sprites.

    Args:
        number: Sprite number used in download filenames
        side_facing: Direction the uploaded side sprite faces ("left" or "right")
        front: Front-facing sprite
        back: Back-facing sprite
        side: Side-facing sprite

    Returns:
        SpritePackage with front, back, icons and spritesheet images

    Raises:
        SpriteCreatorError: If the side facing is invalid or an image fails
    """
    if side_facing not in SIDE_FACINGS:
        raise SpriteCreatorError(
            f"Invalid side facing: {side_facing!r}. Must be 'left' or 'right'."
        )

    try:
        left, right = _resolve_side_pair(side, side_facing)

        return SpritePackage(
            number=number,
            side_facing=side_facing,
            front_sprite=fit_on_transparent_canvas(front, SPRITE_SIZE),
            back_sprite=fit_on_transparent_canvas(back, SPRITE_SIZE),
            icons=tile_horizontally(
                fit_on_transparent_canvas(front, ICON_SIZE), ICON_COPIES
            ),
            spritesheet=stack_vertically(
                [
                    tile_horizontally(
                        fit_on_transparent_canvas(image, ICON_SIZE), SHEET_COPIES
                    )
                    for image in (front, left, right, back)
                ]
            ),
        )
    except SpriteCreatorError:
        raise
    except Exception as exc:
        raise SpriteCreatorError(f"Failed to build sprite set: {exc}") from exc


def fit_on_transparent_canvas(image: Image.Image, size: int) -> Image.Image:
    """Scale an image to fit a square while preserving its aspect ratio.

    The scaled image is centred on a transparent square of ``size`` × ``size``.
    """
    sprite = image.convert("RGBA")
    scale = min(size / sprite.width, size / sprite.height)
    scaled_size = (
        max(1, round(sprite.width * scale)),
        max(1, round(sprite.height * scale)),
    )

    if scaled_size != sprite.size:
        sprite = sprite.resize(scaled_size, Image.Resampling.LANCZOS)

    canvas = Image.new("RGBA", (size, size), _TRANSPARENT)
    offset = ((size - scaled_size[0]) // 2, (size - scaled_size[1]) // 2)
    canvas.paste(sprite, offset)
    return canvas


def mirror(image: Image.Image) -> Image.Image:
    """Return a horizontally flipped copy of the image."""
    return image.convert("RGBA").transpose(Image.Transpose.FLIP_LEFT_RIGHT)


def tile_horizontally(image: Image.Image, copies: int) -> Image.Image:
    """Repeat an image side by side."""
    if copies < 1:
        raise SpriteCreatorError(f"Copies must be at least 1, got {copies}.")

    tile = Image.new("RGBA", (image.width * copies, image.height), _TRANSPARENT)
    for index in range(copies):
        tile.paste(image, (index * image.width, 0))
    return tile


def stack_vertically(rows: Sequence[Image.Image]) -> Image.Image:
    """Stack images top to bottom on a shared canvas."""
    if not rows:
        raise SpriteCreatorError("Cannot stack an empty list of images.")

    sheet = Image.new(
        "RGBA",
        (max(row.width for row in rows), sum(row.height for row in rows)),
        _TRANSPARENT,
    )

    offset = 0
    for row in rows:
        sheet.paste(row, (0, offset))
        offset += row.height
    return sheet


def to_png_bytes(image: Image.Image) -> bytes:
    """Encode an image as PNG bytes."""
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def _resolve_side_pair(
    side: Image.Image, side_facing: str
) -> tuple[Image.Image, Image.Image]:
    """Return the (left, right) sprites, mirroring the uploaded one."""
    if side_facing == "left":
        return side, mirror(side)
    return mirror(side), side


def _parse_sprite_number(filename: str, role: str) -> int:
    """Read the sprite number from a filename such as ``500f.png``."""
    suffix = _ROLE_SUFFIXES[role]
    stem = Path(filename).name

    if stem.lower().endswith(".png"):
        stem = stem[:-4]

    if not stem.lower().endswith(suffix):
        raise SpriteCreatorError(
            f"{filename!r} must end with '{suffix}.png' to be used as the {role} sprite."
        )

    digits = stem[: -len(suffix)]
    if not (digits.isascii() and digits.isdigit()) or int(digits) <= 0:
        raise SpriteCreatorError(
            f"{filename!r} must be named <number>{suffix}.png, e.g. 500{suffix}.png."
        )

    return int(digits)
