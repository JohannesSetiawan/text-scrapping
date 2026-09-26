"""HTTP fetching with anti-bot headers, retries, and backoff."""

from __future__ import annotations

from typing import Optional

import requests

from . import delays, headers
from .errors import ScrapeError
from .models import FetchedPage, ScrapeOptions

_MAX_RETRIES = 2


def fetch(options: ScrapeOptions) -> FetchedPage:
    session = requests.Session()
    delays.jittered_sleep(options.delay_min, options.delay_max)

    last_error: Optional[requests.RequestException] = None
    for attempt in range(_MAX_RETRIES + 1):
        try:
            response = session.get(
                options.url,
                headers=headers.build_headers(options.url),
                timeout=options.timeout,
                allow_redirects=True,
            )
            response.raise_for_status()
            return FetchedPage(
                html=response.text,
                url=response.url,
                status_code=response.status_code,
                content_type=response.headers.get("Content-Type"),
                fetch_method="http",
            )
        except requests.RequestException as exc:
            last_error = exc
            if attempt < _MAX_RETRIES:
                delays.backoff_sleep(attempt)

    raise ScrapeError(_describe_error(last_error))


def _describe_error(exc: Optional[requests.RequestException]) -> str:
    if exc is None:
        return "The request failed for an unknown reason."
    if isinstance(exc, requests.Timeout):
        return "The request timed out."
    if isinstance(exc, requests.TooManyRedirects):
        return "The page redirected too many times."
    if isinstance(exc, requests.SSLError):
        return "The site's SSL/TLS certificate could not be verified."
    if isinstance(exc, requests.HTTPError):
        status = exc.response.status_code if exc.response is not None else "unknown"
        return f"The server responded with HTTP {status} (the request may have been blocked)."
    if isinstance(exc, requests.ConnectionError):
        return "Could not connect to the site. Check the URL and your network."
    return f"The request failed: {exc}"
