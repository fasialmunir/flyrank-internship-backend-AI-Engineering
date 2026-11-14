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