"""URL normalization utilities."""

from urllib.parse import urlparse


def normalize_url(url: str) -> str:
    url = url.strip()
    if url and not urlparse(url).scheme:
        url = "https://" + url
    return url
