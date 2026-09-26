"""Header spoofing: randomized User-Agent and realistic browser headers."""

from __future__ import annotations

import random
from urllib.parse import urlparse

from . import settings

_ACCEPT = (
    "text/html,application/xhtml+xml,application/xml;q=0.9,"
    "image/avif,image/webp,image/apng,*/*;q=0.8,"
    "application/signed-exchange;v=b3;q=0.7"
)


def random_user_agent() -> str:
    return random.choice(settings.USER_AGENTS)


def build_headers(url: str) -> dict[str, str]:
    parsed = urlparse(url)
    referer = (
        f"{parsed.scheme}://{parsed.netloc}/"
        if parsed.scheme and parsed.netloc
        else "https://www.google.com/"
    )

    return {
        "User-Agent": random_user_agent(),
        "Accept": _ACCEPT,
        "Accept-Language": random.choice(settings.ACCEPT_LANGUAGES),
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": referer,
        "DNT": "1",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }
