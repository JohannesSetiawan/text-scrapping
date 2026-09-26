"""Data models shared across the scrapper package."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ScrapeOptions:
    url: str
    extraction_mode: str = "article"          # "article" | "full_page"
    use_browser_fallback: bool = False
    timeout: float = 20.0
    delay_min: float = 0.5
    delay_max: float = 2.0


@dataclass
class FetchedPage:
    html: str
    url: str
    status_code: Optional[int] = None
    content_type: Optional[str] = None
    fetch_method: str = "http"


@dataclass
class Extraction:
    text: str
    title: str = ""
    metadata: dict = field(default_factory=dict)


@dataclass
class ScrapeResult:
    url: str
    title: str
    content: str
    extraction_mode: str
    fetch_method: str
    status_code: Optional[int]
    final_url: str
    metadata: dict = field(default_factory=dict)
