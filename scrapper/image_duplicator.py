"""Image duplication functionality."""

from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO

import requests
from PIL import Image


class ImageDuplicatorError(Exception):
    """Raised when image duplication fails."""


@dataclass
class DuplicateOptions:
    """Options for image duplication."""

    direction: str
    count: int


@dataclass
class DuplicateResult:
    """Result of an image duplication operation."""

    original_image: Image.Image
    duplicated_image: Image.Image
    direction: str
    count: int
    original_size: tuple[int, int]
    new_size: tuple[int, int]


def duplicate_image(image: Image.Image, options: DuplicateOptions) -> DuplicateResult:
    """Duplicate an image horizontally or vertically.

    Args:
        image: PIL Image object to duplicate
        options: Duplication options including direction and count

    Returns:
        DuplicateResult containing original and duplicated images

    Raises:
        ImageDuplicatorError: If duplication fails or invalid options provided
    """
    if options.direction not in ("horizontal", "vertical"):
        raise ImageDuplicatorError(
            f"Invalid direction: {options.direction}. Must be 'horizontal' or 'vertical'"
        )

    if options.count < 1:
        raise ImageDuplicatorError(f"Count must be at least 1, got {options.count}")

    try:
        original_size = image.size
        width, height = original_size

        if options.direction == "horizontal":
            new_image = Image.new(image.mode, (width * options.count, height))
            for i in range(options.count):
                new_image.paste(image, (i * width, 0))
            new_size = (width * options.count, height)

        else:
            new_image = Image.new(image.mode, (width, height * options.count))
            for i in range(options.count):
                new_image.paste(image, (0, i * height))
            new_size = (width, height * options.count)

        return DuplicateResult(
            original_image=image,
            duplicated_image=new_image,
            direction=options.direction,
            count=options.count,
            original_size=original_size,
            new_size=new_size,
        )

    except ImageDuplicatorError:
        raise
    except Exception as exc:
        raise ImageDuplicatorError(f"Failed to duplicate image: {exc}") from exc


def load_image_from_url(url: str, timeout: int = 20) -> Image.Image:
    """Load an image from a URL.

    Args:
        url: Image URL
        timeout: Request timeout in seconds

    Returns:
        PIL Image object

    Raises:
        ImageDuplicatorError: If image cannot be loaded
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()

        image = Image.open(BytesIO(response.content))
        return image

    except Exception as exc:
        raise ImageDuplicatorError(f"Failed to load image from URL: {exc}") from exc


def load_image_from_bytes(image_bytes: bytes) -> Image.Image:
    """Load an image from bytes.

    Args:
        image_bytes: Image file bytes

    Returns:
        PIL Image object

    Raises:
        ImageDuplicatorError: If image cannot be loaded
    """
    try:
        image = Image.open(BytesIO(image_bytes))
        return image

    except Exception as exc:
        raise ImageDuplicatorError(f"Failed to load image from bytes: {exc}") from exc
