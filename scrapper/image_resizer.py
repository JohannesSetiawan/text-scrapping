"""Image resizing functionality."""

from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO

import requests
from PIL import Image


class ImageResizerError(Exception):
    """Raised when image resizing fails."""


@dataclass
class ResizeOptions:
    """Options for image resizing."""

    width: int
    height: int
    maintain_aspect_ratio: bool = False


@dataclass
class ResizeResult:
    """Result of an image resize operation."""

    original_image: Image.Image
    resized_image: Image.Image
    original_size: tuple[int, int]
    new_size: tuple[int, int]
    aspect_ratio_maintained: bool


def resize_image(image: Image.Image, options: ResizeOptions) -> ResizeResult:
    """Resize an image according to the given options.

    Args:
        image: PIL Image object to resize
        options: Resize options including dimensions and aspect ratio setting

    Returns:
        ResizeResult containing original and resized images with metadata

    Raises:
        ImageResizerError: If resizing fails
    """
    try:
        original_size = image.size

        if options.maintain_aspect_ratio:
            new_size = _calculate_aspect_ratio_size(
                original_size, options.width, options.height
            )
        else:
            new_size = (options.width, options.height)

        resized_image = image.resize(new_size, Image.Resampling.LANCZOS)

        return ResizeResult(
            original_image=image,
            resized_image=resized_image,
            original_size=original_size,
            new_size=new_size,
            aspect_ratio_maintained=options.maintain_aspect_ratio,
        )

    except Exception as exc:
        raise ImageResizerError(f"Failed to resize image: {exc}") from exc


def _calculate_aspect_ratio_size(
    original_size: tuple[int, int], target_width: int, target_height: int
) -> tuple[int, int]:
    """Calculate new size maintaining aspect ratio.

    Fits the image within the target dimensions while preserving aspect ratio.

    Args:
        original_size: Original (width, height)
        target_width: Target width
        target_height: Target height

    Returns:
        New (width, height) that fits within target dimensions
    """
    orig_width, orig_height = original_size
    aspect_ratio = orig_width / orig_height

    if target_width / target_height > aspect_ratio:
        new_height = target_height
        new_width = int(target_height * aspect_ratio)
    else:
        new_width = target_width
        new_height = int(target_width / aspect_ratio)

    return (new_width, new_height)


def load_image_from_url(url: str, timeout: int = 20) -> Image.Image:
    """Load an image from a URL.

    Args:
        url: Image URL
        timeout: Request timeout in seconds

    Returns:
        PIL Image object

    Raises:
        ImageResizerError: If image cannot be loaded
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
        raise ImageResizerError(f"Failed to load image from URL: {exc}") from exc


def load_image_from_bytes(image_bytes: bytes) -> Image.Image:
    """Load an image from bytes.

    Args:
        image_bytes: Image file bytes

    Returns:
        PIL Image object

    Raises:
        ImageResizerError: If image cannot be loaded
    """
    try:
        image = Image.open(BytesIO(image_bytes))
        return image

    except Exception as exc:
        raise ImageResizerError(f"Failed to load image from bytes: {exc}") from exc
