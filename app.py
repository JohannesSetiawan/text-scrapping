"""Streamlit UI for the text scrapper."""

from __future__ import annotations

import json

import streamlit as st

from scrapper import ScrapeError, ScrapeOptions, scrape
from scrapper.urls import normalize_url

_EXTRACTION_LABELS = {
    "article": "Article (main content only)",
    "full_page": "Full page (all visible text)",
}


def main() -> None:
    st.set_page_config(page_title="Text Scrapper", page_icon="🕸️", layout="wide")

    st.title("🕸️ Text Scrapper")
    st.caption(
        "Scrape readable text from any website with rotating user agents, "
        "header spoofing, and rate-limit protection."
    )

    url, settings = render_settings()

    if st.button("Scrape", type="primary"):
        run_scrape(url, settings)

    render_result()

    st.caption(
        "Use responsibly: respect each site's robots.txt and terms of service, "
        "and only scrape content you are allowed to access."
    )


def render_settings() -> tuple[str, dict]:
    with st.sidebar:
        st.header("Settings")

        st.subheader("Extraction")
        extraction_mode = st.radio(
            "Extraction mode",
            options=list(_EXTRACTION_LABELS),
            format_func=lambda mode: _EXTRACTION_LABELS[mode],
            index=0,
        )
        use_browser_fallback = st.checkbox(
            "Browser fallback for JavaScript pages",
            value=False,
            help=(
                "If the HTTP request returns no usable text, re-render the page "
                "with a real headless browser."
            ),
        )

        st.divider()
        st.subheader("Anti-bot protections")
        st.caption("Applied automatically on every request.")
        st.checkbox("Rotating User-Agent", value=True, disabled=True)
        st.checkbox("Realistic header spoofing", value=True, disabled=True)
        st.checkbox("Randomized request delays", value=True, disabled=True)

        st.divider()
        st.subheader("Advanced")
        timeout = st.slider("Request timeout (s)", min_value=5, max_value=60, value=20)
        delay_min, delay_max = st.slider(
            "Delay range (s)",
            min_value=0.0,
            max_value=10.0,
            value=(0.5, 2.0),
        )

    url = st.text_input("Website URL", placeholder="https://example.com/article")
    return url, {
        "extraction_mode": extraction_mode,
        "use_browser_fallback": use_browser_fallback,
        "timeout": float(timeout),
        "delay_min": float(delay_min),
        "delay_max": float(delay_max),
    }


def run_scrape(url: str, settings: dict) -> None:
    url = normalize_url(url)
    if not url:
        st.warning("Please enter a URL to scrape.")
        return

    options = ScrapeOptions(url=url, **settings)
    try:
        with st.spinner("Scraping the page..."):
            result = scrape(options)
    except ScrapeError as exc:
        st.session_state["scrape_error"] = str(exc)
        st.session_state["scrape_result"] = None
        return

    st.session_state["scrape_result"] = result
    st.session_state["scrape_error"] = None


def render_result() -> None:
    error = st.session_state.get("scrape_error")
    result = st.session_state.get("scrape_result")

    if error:
        st.error(error)
    if result is None:
        return

    st.divider()
    st.subheader(result.title or "Scraped content")
    render_metrics(result)

    st.markdown("**Extracted text**")
    st.caption("Use the copy icon (top-right of the box) to copy everything.")
    st.code(result.content, language=None)
    st.download_button(
        "Download .txt",
        data=result.content,
        file_name="scraped_text.txt",
        mime="text/plain",
    )

    with st.expander("View / copy JSON result"):
        payload = json.dumps(result_to_dict(result), indent=2)
        st.code(payload, language="json")
        st.download_button(
            "Download .json",
            data=payload,
            file_name="scraped_text.json",
            mime="application/json",
        )


def render_metrics(result) -> None:
    metadata = result.metadata
    word_count = metadata.get("word_count", 0)
    char_count = metadata.get("char_count", 0)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Fetch method", result.fetch_method.upper())
    col2.metric("Extraction", "Article" if result.extraction_mode == "article" else "Full page")
    col3.metric("Words", f"{word_count:,}")
    col4.metric("Characters", f"{char_count:,}")

    details = []
    if result.status_code is not None:
        details.append(f"Status: {result.status_code}")
    details.append(f"Final URL: {result.final_url}")
    st.caption(" · ".join(details))


def result_to_dict(result) -> dict:
    return {
        "url": result.url,
        "final_url": result.final_url,
        "title": result.title,
        "content": result.content,
        "extraction_mode": result.extraction_mode,
        "fetch_method": result.fetch_method,
        "status_code": result.status_code,
        "metadata": result.metadata,
    }


if __name__ == "__main__":
    main()
