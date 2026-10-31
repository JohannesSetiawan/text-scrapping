# 🕸️ Text Scrapper & 🎨 AI Image Generation

A Streamlit app with two main features:

1. **Text Scrapper** — scrapes readable text from any website with built-in protections to help bypass basic bot detection and rate limiting.
2. **AI Image Generation** — generate images using OpenAI-compatible API (gpt-image-2 or gpt-image-2.5 models).

## Features

### Text Scrapper
- **Two extraction modes**
  - *Article* — pulls the main content using readability parsing (trafilatura), dropping navigation, ads, and footers.
  - *Full page* — returns every visible text node on the page.
- **JavaScript fallback** — if the plain HTTP request returns no usable text, the page can be re-rendered with a real headless browser (Playwright).
- **Anti-bot protections** (applied automatically on every request)
  - Rotating realistic User-Agent strings.
  - Realistic header spoofing (Accept, Accept-Language, Referer, Sec-Fetch-*, etc.).
  - Randomized request delays with jitter and exponential backoff.
- **Output** — plain text (with a one-click copy button) and a JSON view (title, URL, content, metadata).

### AI Image Generation
- **Model selection** — choose between gpt-image-2 and gpt-image-2.5
- **Configurable settings**
  - Image size (1024x1024, 1024x1792, 1792x1024, 512x512, 256x256)
  - Number of images per prompt (1-4)
  - Quality level (standard or HD)
- **Output** — images displayed inline with download buttons
- No database — everything is in-memory.

## Project structure

```
text-scrapper/
├── app.py                          # Main Streamlit page (Text Scrapper)
├── requirements.txt
├── .env                            # Environment variables (API_URL, API_KEY)
├── .env.example                    # Example environment file
├── pages/
│   └── 1_🎨_Image_Generation.py   # Image generation page
└── scrapper/
    ├── __init__.py
    ├── models.py                   # Data models
    ├── settings.py                 # Config and static assets
    ├── headers.py                  # User-Agent rotation + header spoofing
    ├── delays.py                   # Jittered delays + backoff
    ├── urls.py                     # URL normalization
    ├── errors.py                   # ScrapeError
    ├── http_fetcher.py             # HTTP fetching
    ├── browser_fetcher.py          # Playwright fallback
    ├── extractors.py               # Article / full-page extraction
    ├── scraper.py                  # Orchestration
    └── image_generator.py          # Image generation logic
```

## Setup

1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
# activate the virtual environment, then:
pip install -r requirements.txt
```

2. Configure environment variables for image generation:

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your API credentials:
# API_URL=https://your-api-endpoint.com/v1
# API_KEY=your_api_key_here
```

3. (Optional) Install Playwright for the browser fallback in text scraping:

```bash
pip install playwright
playwright install chromium
```

## Run

```bash
streamlit run app.py
```

## Usage

### Text Scrapper
1. From the main page, enter a URL.
2. Choose an extraction mode.
3. Optionally enable the browser fallback for JavaScript-heavy sites.
4. Click **Scrape**.
5. Copy the text with the copy button or download it as `.txt` / `.json`.

### Image Generation
1. Navigate to the **🎨 Image Generation** page from the sidebar.
2. Select your preferred model (gpt-image-2 or gpt-image-2.5).
3. Configure image size, number of images, and quality settings.
4. Enter your image prompt.
5. Click **Generate Images**.
6. View the generated images and download them individually.

## Disclaimer

Use responsibly. Respect each site's `robots.txt` and terms of service, and only
scrape content you are permitted to access.
