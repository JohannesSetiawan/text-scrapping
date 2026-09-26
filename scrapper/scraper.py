"""High-level scraping orchestration: HTTP first, optional browser fallback, then extraction."""

from __future__ import annotations

from datetime import datetime, timezone

from . import browser_fetcher, extractors, http_fetcher
from .errors import ScrapeError
from .models import Extraction, FetchedPage, ScrapeOptions, ScrapeResult
from .settings import MIN_MEANINGFUL_CHARS
from .urls import normalize_url


def scrape(options: ScrapeOptions) -> ScrapeResult:
    options.url = normalize_url(options.url)

    page, extraction, http_error, extraction_error = _try_http(options)

    if options.use_browser_fallback and _needs_fallback(extraction, http_error):
        page, extraction, http_error, extraction_error = _try_browser(options)

    if extraction is None or not extraction.text.strip():
        if extraction_error is not None:
            raise extraction_error
        if http_error is not None:
            raise http_error
        raise ScrapeError("No extractable text was found on the page.")

    return ScrapeResult(
        url=options.url,
        title=extraction.title,
        content=extraction.text,
        extraction_mode=options.extraction_mode,
        fetch_method=page.fetch_method,
        status_code=page.status_code,
        final_url=page.url,
        metadata=_build_metadata(extraction, page),
    )


def _try_http(options: ScrapeOptions):
    try:
        page = http_fetcher.fetch(options)
    except ScrapeError as exc:
        return None, None, exc, None

    try:
        extraction = extractors.extract(options.extraction_mode, page.html, page.url)
    except ScrapeError as exc:
        return page, Extraction(text=""), None, exc

    return page, extraction, None, None


def _try_browser(options: ScrapeOptions):
    page = browser_fetcher.fetch(options)

    try:
        extraction = extractors.extract(options.extraction_mode, page.html, page.url)
    except ScrapeError as exc:
        return page, Extraction(text=""), None, exc

    return page, extraction, None, None


def _needs_fallback(extraction, http_error) -> bool:
    if http_error is not None:
        return True
    if extraction is None:
        return True
    return len(extraction.text.strip()) < MIN_MEANINGFUL_CHARS


def _build_metadata(extraction: Extraction, page: FetchedPage) -> dict:
    metadata = dict(extraction.metadata)
    metadata.update({
        "word_count": len(extraction.text.split()),
        "char_count": len(extraction.text),
        "content_type": page.content_type,
        "scraped_at": datetime.now(timezone.utc).isoformat(),
    })
    return metadata
