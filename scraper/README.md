
# Polite Scraper — FlyRank Internship

## Project Overview

A Python web scraping pipeline built for FlyRank Backend Internship, Week 5, Assignment A9.

The scraper collects 60 books from the Books to Scrape practice website, extracts book information, normalizes and validates records, and saves the results as JSON.

## Target Classification

- **Target:** https://books.toscrape.com/
- **Website Information:** https://toscrape.com/
- **Purpose:** Books to Scrape is a practice sandbox designed for learning and testing web scraping.
- **Scope:** First 3 catalogue pages (60 books).
- **Data Collected:** Title, price, availability, rating, description, book URL, and image URL.
- **Robots.txt:** HTTP 404 Not Found (no robots file found).

I will not reuse this code on another site without checking its rules and terms first.

## Technology Stack

- Python 3.10+
- Requests
- Beautiful Soup
- Pydantic
- Built-in JSON module
- Git and GitHub

## Project Structure

```text
scraper/
├── cache/
├── output/
│   ├── books.json
│   ├── errors.json
│   └── run-report.json
├── src/
│   └── main.py
├── .gitignore
├── requirements.txt
└── README.md
```

## Installation and Usage

### 1. Clone the Repository

```bash
git https://github.com/fasialmunir/flyrank-internship-backend-AI-Engineering
cd flyrank-internship-backend-AI-Engineering/scraper
```

### 2. Create and Activate a Virtual Environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Scraper

```bash
python src/main.py
```

The scraper generates the following files:

- `output/books.json`
- `output/errors.json`
- `output/run-report.json`

## Record Schema

Each validated book record contains:

| Field | Type |
|---|---|
| `title` | string |
| `product_url` | string |
| `price_text` | string |
| `price_gbp` | float |
| `availability_text` | string |
| `rating_text` | string |
| `rating` | integer |
| `description` | string or null |
| `source_page` | string |
| `fetched_at` | string (UTC) |

## Responsible Scraping

- Uses an identifying User-Agent.
- Sets a 10-second request timeout.
- Waits at least 0.5 seconds between real requests.
- Caches downloaded HTML to avoid unnecessary requests.
- Retries temporary timeouts and HTTP 5xx errors once.
- Does not retry HTTP 403 or 404.
- Validates records before storing them.
- Logs failed pages instead of stopping the entire run.

## Validation and Run Evidence

The following is a real run report from the project:

### Run Report

```json
{
    "started_at": "2026-11-14T08:43:06Z",
    "duration_seconds": 1.52,
    "pages_fetched": 0,
    "cache_hits": 63,
    "valid_records": 60,
    "invalid_records": 0,
    "failed_pages": 0
}
```

### Results

- **Catalogue pages:** 3
- **Unique books:** 60
- **Valid records:** 60
- **Invalid records:** 0
- **Failed pages:** 0

The report shows that all 63 successful page loads came from cache during this run.

## Why No Browser Was Needed

The required book information is already available in the HTML returned by the server. A browser would only add unnecessary complexity and cost.

## Ethical Considerations

- Use an official API whenever one is available.
- Never bypass logins, paywalls, or access restrictions.
- Collect only the data needed for the task.
- Respect the website's rules and terms.

## Limitation

The scraper is designed specifically for the Books to Scrape practice website. Changes to its HTML structure or CSS selectors may require code updates.

## Internship Progress

-  Stage 0: Target classification
-  Stage 1: Fetch and cache HTML
-  Stage 2: Discover three catalogue pages
-  Stage 3: Extract raw book records
-  Stage 4: Normalize and validate records
-  Stage 5: Handle failures and generate reports
-  Stage 6: Publish project and evidence

---
