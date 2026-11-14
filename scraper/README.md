# Polite Scraper — FlyRank Internship

## Project Overview

A Python web scraping project for **FlyRank Backend Internship — Week 5, Assignment A9**.

It collects, cleans, validates, and stores book data as JSON.

---

## Target Classification

- **Target:** https://books.toscrape.com/
- **Website Information:** https://toscrape.com/
- **Purpose:** Books to Scrape is a practice sandbox designed for learning and testing web scraping.
- **Scope:** First 3 catalogue pages (60 books).
## Sample Book Data

| Field | Value |
|---|---|
| Title | A Light in the Attic |
| Price | £51.77 |
| Availability | In stock (22 available) |
| Rating | 3 Star |
| Book URL | [View Book](https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html) |
| Image URL | [View Image](https://books.toscrape.com/media/cache/fe/72/fe72f0532301ec28892ae79a629a293c.jpg) |

---

## Robots.txt Check

- **URL:** https://books.toscrape.com/robots.txt
- **Result:** HTTP 404 Not Found.
- **Finding:** No robots file found.

No robots.txt file is not treated as permission by itself.

**Responsible Scraping:** I will not reuse this code on another site without checking its rules and terms first.

---

## Technology Stack

- Python 3.10+
- Requests
- Beautiful Soup
- Pydantic
- JSON
- Git and GitHub

---

## Project Structure

```text
scraper/
├── README.md
├── .gitignore
└── src/
    └── main.py

```
## Stage 1 — Fetch and Cache HTML

Used Python Requests to download the first catalogue page.

- Added a custom `User-Agent` and a 10-second request timeout.
- Checked the HTTP status code before processing the response.
- Saved the HTML locally in `cache/catalogue-page-1.html`.
- Implemented caching to avoid repeated website requests.

### Checkpoint Results

| Metric | Result |
|---|---|
| First run | FETCH |
| Second run | CACHE HIT |
| Response size | 51,294 bytes |

---

## Stage 2 — Discover Three Catalogue Pages

- Used Beautiful Soup to parse catalogue HTML.
- Extracted book links using CSS selectors.
- Converted relative URLs into absolute URLs using `urljoin()`.
- Followed the website's Next link to discover pages 2 and 3.
- Added a 0.5-second delay before real network requests.
- Cached all three catalogue pages.
- Removed duplicate URLs while preserving order.

### Checkpoint Results

| Metric | Result |
|---|---:|
| Catalogue pages | 3 |
| Discovered books | 60 |
| Unique URLs | 60 |
| Books per page | 20 |

### Cache Verification

The second run loaded all three catalogue pages from cache and produced the same results without making repeated website requests.

---

## Stage 3 — Extract Raw Book Records

Used Beautiful Soup to extract information from all 60 individual book pages.

- Collected eight raw fields:
  - Title
  - Product URL
  - Price
  - Availability
  - Rating
  - Description
  - Source page
  - Fetch timestamp
- Targeted the product information section using CSS selectors.
- Cached each book's HTML to avoid repeated requests.
- Used a custom `User-Agent`, request timeout, and 0.5-second delay.
- Stored missing descriptions as `null`.
- Preserved `source_page` and `fetched_at` as data provenance.

### Checkpoint Results

| Metric | Result |
|---|---:|
| Individual detail pages processed | 60 |
| Complete raw records printed | 1 |
| Cached pages reused | Yes |

### Cache Verification

Cached individual book pages were reused on subsequent runs to avoid unnecessary network requests.

---

## Stage 4 — Normalize, Validate and Store Data

- Installed and used Pydantic to define the book record schema.
- Converted price text (e.g., `£51.77`) into a numeric `price_gbp` value.
- Converted star ratings into integers (1–5).
- Preserved original raw values alongside normalized values.
- Validated records before storing them.
- Used absolute HTTPS URLs for product identity.
- Saved valid records to `output/books.json`.
- Saved invalid records and error reasons to `output/errors.json`.
- Removed duplicate product URLs to ensure idempotent runs.

### Checkpoint Results

| Metric | Expected Result |
|---|---:|
| Valid records | 60 |
| Duplicate records | 0 |
| Records after second run | 60 |

### Validation and Storage Verification

All records are validated before storage. Duplicate product URLs are removed to ensure that repeated runs do not create duplicate records.

The second run should still contain exactly 60 valid records.

---

## Stage 5 — Failure Handling and Run Reporting

- Added error handling to process each book page independently.
- Implemented one retry for request timeouts and HTTP 5xx errors.
- Avoided retries for HTTP 403 and 404 responses.
- Logged failed pages without stopping the scraper.
- Generated `output/run-report.json` containing:
  - Start time
  - Duration
  - Cache hits
  - Pages fetched
  - Valid records
  - Invalid records
  - Failed pages
- Tested failure handling using a fake URL (`example.invalid`).
- Removed the fake URL after successfully testing failure handling.

### Checkpoint Results

| Metric | Result |
|---|---:|
| Valid records | 60 |
| Failed pages during test | 1 |
| Invalid records | 0 |
| Cache hits | 63 |
| Run report generated | Successfully |

### Failure Handling Verification

The scraper continued processing all valid books despite the simulated failure.

The failed page was logged without interrupting the scraping process.

---

    