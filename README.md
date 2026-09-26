# 🕸️ Text Scrapper

A Streamlit app that scrapes readable text from any website, with built-in
protections to help bypass basic bot detection and rate limiting.

## Features

- **Two extraction modes**
  - *Article* — pulls the main content using readability parsing (trafilatura), dropping navigation, ads, and footers.
  - *Full page* — returns every visible text node on the page.
- **JavaScript fallback** — if the plain HTTP request returns no usable text, the page can be re-rendered with a real headless browser (Playwright).
- **Anti-bot protections** (applied automatically on every request)
  - Rotating realistic User-Agent strings.
  - Realistic header spoofing (Accept, Accept-Language, Referer, Sec-Fetch-*, etc.).
  - Randomized request delays with jitter and exponential backoff.
- **Output** — plain text (with a one-click copy button) and a JSON view (title, URL, content, metadata).
- No database — everything is in-memory.

## Project structure

```
text-scrapper/
├── app.py                 # Streamlit UI
├── requirements.txt
└── scrapper/
    ├── __init__.py
    ├── models.py          # Data models
    ├── settings.py        # Config and static assets
    ├── headers.py         # User-Agent rotation + header spoofing
    ├── delays.py          # Jittered delays + backoff
    ├── urls.py            # URL normalization
    ├── errors.py          # ScrapeError
    ├── http_fetcher.py    # HTTP fetching
    ├── browser_fetcher.py # Playwright fallback
    ├── extractors.py      # Article / full-page extraction
    └── scraper.py         # Orchestration
```

## Setup

```bash
python -m venv .venv
# activate the virtual environment, then:
pip install -r requirements.txt
```

The browser fallback is optional. If you enable it, install the browser runtime once:

```bash
pip install playwright
playwright install chromium
```

## Run

```bash
streamlit run app.py
```

## Usage

1. Enter a URL.
2. Choose an extraction mode.
3. Optionally enable the browser fallback for JavaScript-heavy sites.
4. Click **Scrape**.
5. Copy the text with the copy button or download it as `.txt` / `.json`.

## Disclaimer

Use responsibly. Respect each site's `robots.txt` and terms of service, and only
scrape content you are permitted to access.
