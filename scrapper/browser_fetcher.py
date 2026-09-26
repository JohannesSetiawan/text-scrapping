"""Headless-browser fetching via Playwright for JavaScript-heavy or protected pages."""

from __future__ import annotations

from . import headers
from .errors import ScrapeError
from .models import FetchedPage, ScrapeOptions


def fetch(options: ScrapeOptions) -> FetchedPage:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise ScrapeError(
            "Browser fallback requires Playwright. Install it with "
            "`pip install playwright` and `playwright install chromium`."
        ) from exc

    user_agent = headers.random_user_agent()
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                ],
            )
            try:
                context = browser.new_context(
                    user_agent=user_agent,
                    locale="en-US",
                    viewport={"width": 1366, "height": 768},
                )
                page = context.new_page()
                try:
                    page.goto(
                        options.url,
                        wait_until="domcontentloaded",
                        timeout=int(options.timeout * 1000),
                    )
                except Exception:
                    # A navigation timeout may still leave a partially rendered DOM.
                    pass
                html = page.content()
                final_url = page.url
            finally:
                browser.close()
    except ScrapeError:
        raise
    except Exception as exc:
        raise ScrapeError(f"Browser rendering failed: {exc}") from exc

    return FetchedPage(
        html=html,
        url=final_url,
        status_code=None,
        content_type="text/html",
        fetch_method="browser",
    )
