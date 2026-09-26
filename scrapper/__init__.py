"""Text-scrapper package: fetch and extract text from web pages."""

from .errors import ScrapeError
from .models import Extraction, FetchedPage, ScrapeOptions, ScrapeResult
from .scraper import scrape

__all__ = [
    "ScrapeError",
    "Extraction",
    "FetchedPage",
    "ScrapeOptions",
    "ScrapeResult",
    "scrape",
]
