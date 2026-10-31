"""Image generation using OpenAI-compatible API."""

from __future__ import annotations

import base64
import os
from dataclasses import dataclass
from io import BytesIO
from typing import Optional

import requests
from dotenv import load_dotenv
from PIL import Image

load_dotenv()


@dataclass
class ImageGenerationOptions:
    prompt: str
    model: str = "gpt-image-2"
    size: str = "1024x1024"
    n: int = 1
    quality: str = "standard"


@dataclass
class GeneratedImage:
    image: Image.Image
    prompt: str
    model: str
    size: str
    revised_prompt: Optional[str] = None


class ImageGenerationError(Exception):
    pass


def generate_images(options: ImageGenerationOptions) -> list[GeneratedImage]:
    api_url = os.getenv("API_URL")
    api_key = os.getenv("API_KEY")

    if not api_url:
        raise ImageGenerationError("API_URL not found in environment variables")
    if not api_key:
        raise ImageGenerationError("API_KEY not found in environment variables")

    endpoint = f"{api_url.rstrip('/')}/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": options.model,
        "prompt": options.prompt,
        "n": options.n,
        "size": options.size,
        "quality": options.quality,
        "response_format": "b64_json",
    }

    try:
        response = requests.post(endpoint, json=payload, headers=headers, timeout=120)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        raise ImageGenerationError("Request timed out. The API took too long to respond.")
    except requests.exceptions.ConnectionError:
        raise ImageGenerationError("Failed to connect to the API. Check your API_URL.")
    except requests.exceptions.HTTPError as exc:
        error_detail = _extract_error_message(response)
        raise ImageGenerationError(
            f"API request failed with status {response.status_code}: {error_detail}"
        ) from exc
    except requests.exceptions.RequestException as exc:
        raise ImageGenerationError(f"Request failed: {str(exc)}") from exc

    try:
        data = response.json()
    except ValueError as exc:
        raise ImageGenerationError("Invalid JSON response from API") from exc

    if "data" not in data:
        raise ImageGenerationError("API response missing 'data' field")

    images = []
    for item in data["data"]:
        if "b64_json" not in item:
            raise ImageGenerationError("API response missing 'b64_json' field")

        try:
            image_data = base64.b64decode(item["b64_json"])
            image = Image.open(BytesIO(image_data))
        except Exception as exc:
            raise ImageGenerationError(f"Failed to decode image: {str(exc)}") from exc

        revised_prompt = item.get("revised_prompt")

        images.append(
            GeneratedImage(
                image=image,
                prompt=options.prompt,
                model=options.model,
                size=options.size,
                revised_prompt=revised_prompt,
            )
        )

    return images


def _extract_error_message(response: requests.Response) -> str:
    try:
        error_data = response.json()
        if "error" in error_data:
            if isinstance(error_data["error"], dict):
                return error_data["error"].get("message", str(error_data["error"]))
            return str(error_data["error"])
        return response.text[:200]
    except ValueError:
        return response.text[:200]
