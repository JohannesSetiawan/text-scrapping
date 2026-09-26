"""Text extraction: article mode (readability) and full-page mode (BeautifulSoup)."""

from __future__ import annotations

from bs4 import BeautifulSoup

from .errors import ScrapeError
from .models import Extraction

_NON_CONTENT_TAGS = [
    "script", "style", "noscript", "svg", "template", "iframe",
    "head", "meta", "link", "base",
]


def extract(mode: str, html: str, url: str) -> Extraction:
    if mode == "article":
        return _extract_article(html, url)
    return _extract_full_page(html, url)


def _extract_article(html: str, url: str) -> Extraction:
    try:
        import trafilatura
    except ImportError as exc:
        raise ScrapeError(
            "Article extraction requires the 'trafilatura' package. "
            "Install it with `pip install trafilatura`, or switch to full-page mode."
        ) from exc

    try:
        text = trafilatura.extract(
            html,
            url=url,
            include_comments=False,
            include_tables=True,
            output_format="txt",
        )
    except Exception as exc:
        raise ScrapeError(f"Article extraction failed: {exc}") from exc

    text = (text or "").strip()
    if not text:
        raise ScrapeError(
            "No article content could be identified. The page may require JavaScript, "
            "or try switching to full-page mode."
        )

    title, metadata = _article_metadata(html)
    return Extraction(text=text, title=title or _fallback_title(html), metadata=metadata)


def _article_metadata(html: str) -> tuple[str, dict]:
    try:
        import trafilatura
        document = trafilatura.extract_metadata(html)
    except Exception:
        return "", {}

    if not document:
        return "", {}

    title = (document.get("title") or "").strip()
    metadata = {
        field: document.get(field)
        for field in ("author", "date", "sitename", "language", "description")
        if document.get(field)
    }
    return title, metadata


def _extract_full_page(html: str, url: str) -> Extraction:
    soup = BeautifulSoup(html, "lxml")
    title = _title_from_soup(soup)
    description = _meta_description(soup)

    for tag in soup.find_all(_NON_CONTENT_TAGS):
        tag.decompose()

    text = soup.get_text(separator="\n", strip=True)
    metadata = {}
    if description:
        metadata["description"] = description

    return Extraction(text=text, title=title, metadata=metadata)


def _fallback_title(html: str) -> str:
    return _title_from_soup(BeautifulSoup(html, "lxml"))


def _title_from_soup(soup: BeautifulSoup) -> str:
    if soup.title and soup.title.string:
        return soup.title.string.strip()
    heading = soup.find("h1")
    if heading:
        return heading.get_text(strip=True)
    return ""


def _meta_description(soup: BeautifulSoup) -> str:
    tag = soup.find("meta", attrs={"name": "description"})
    if tag and tag.get("content"):
        return tag["content"].strip()
    return ""
