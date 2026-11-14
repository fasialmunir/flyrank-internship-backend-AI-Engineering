import re
from urllib.parse import urlparse
from pydantic import BaseModel
from pathlib import Path
from urllib.parse import urljoin
import time
from datetime import datetime, timezone
import hashlib
import requests
from bs4 import BeautifulSoup
import json
# ---------------------------------
# 1. WEBSITE CONFIGURATION
# ---------------------------------

BASE_URL = "https://books.toscrape.com/"

USER_AGENT = (
    "FlyRankInternshipA9/1.0 "
    "(+https://github.com/YOUR-USERNAME/YOUR-REPOSITORY)"
)

HEADERS = {
    "User-Agent": USER_AGENT
}
TIMEOUT = 10
REQUEST_DELAY = 0.5


# ---------------------------------
# STAGE 4: DATA SCHEMA
# ---------------------------------

class BookRecord(BaseModel):
    title: str
    product_url: str
    price_text: str
    price_gbp: float
    availability_text: str
    rating_text: str
    rating: int
    description: str | None = None
    source_page: str
    fetched_at: str

# ---------------------------------
# STAGE 5: RUN TRACKING
# ---------------------------------

RUN_STATS = {
    "pages_fetched": 0,
    "cache_hits": 0,
    "valid_records": 0,
    "invalid_records": 0,
    "failed_pages": 0
}
# ---------------------------------
# 2. PROJECT PATHS
# ---------------------------------

PROJECT_DIR = Path(__file__).resolve().parents[1]
CACHE_DIR = PROJECT_DIR / "cache"

# ---------------------------------
# 3. FETCH AND CACHE CATALOGUE
# ---------------------------------


def get_page_html(url, page_number):

    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    cache_file = CACHE_DIR / f"catalogue-page-{page_number}.html"

    # Check cache first
    if cache_file.exists():

        html = cache_file.read_bytes()

        RUN_STATS["cache_hits"] += 1

        print(f"CACHE HIT: page {page_number}")
        print(f"Response size: {len(html)} bytes")

        return html

    # Fetch from website
    print(f"FETCH: page {page_number}")

    time.sleep(REQUEST_DELAY)

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=TIMEOUT
        )

        if response.status_code != 200:
            print(f"Fetch failed: HTTP {response.status_code}")
            RUN_STATS["failed_pages"] += 1
            return None

        html = response.content

        cache_file.write_bytes(html)

        # Update successful network request counter
        RUN_STATS["pages_fetched"] += 1

        print(f"Response size: {len(html)} bytes")
        print(f"Saved: {cache_file}")

        return html

    except requests.Timeout as error:
        print(f"Request timed out: {error}")
        RUN_STATS["failed_pages"] += 1
        return None

    except requests.RequestException as error:
        print(f"Request failed: {error}")
        RUN_STATS["failed_pages"] += 1
        return None


# ---------------------------------
# 4. DISCOVER BOOK LINKS
# ---------------------------------

def discover_book_links(html, page_url):

    soup = BeautifulSoup(html, "html.parser")

    book_urls = []

    for book in soup.select("article.product_pod h3 a"):

        href = book.get("href")

        if href:
            absolute_url = urljoin(page_url, href)
            book_urls.append(absolute_url)

    next_link = soup.select_one("li.next a")

    next_url = None

    if next_link and next_link.get("href"):
        next_url = urljoin(page_url, next_link["href"])

    return book_urls, next_url


def discover_catalogue():

    current_url = BASE_URL
    discovered = []
    catalogue_pages = 0

    for page_number in range(1, 4):

        html = get_page_html(current_url, page_number)

        if html is None:
            break

        book_urls, next_url = discover_book_links(
            html,
            current_url
        )

        # Keep the book URL and its source catalogue page
        for book_url in book_urls:
            discovered.append((book_url, current_url))

        catalogue_pages += 1

        print(
            f"Page {page_number}: "
            f"discovered {len(book_urls)} book links"
        )

        if page_number == 3:
            break

        if not next_url:
            print("Next link not found.")
            break

        current_url = next_url

    # Remove duplicate book URLs, preserving their source page
    unique = {}

    for book_url, source_page in discovered:
        if book_url not in unique:
            unique[book_url] = source_page

    print("\n--- Catalogue Report ---")
    print(f"catalogue_pages={catalogue_pages}")
    print(f"discovered={len(discovered)}")
    print(f"unique_urls={len(unique)}")

    return list(unique.items())


# ---------------------------------
# 5. FETCH AND CACHE BOOK DETAILS
# ---------------------------------


def fetch_book_page(product_url):

    url_hash = hashlib.sha256(
        product_url.encode("utf-8")
    ).hexdigest()

    cache_file = CACHE_DIR / f"book-{url_hash}.html"
    metadata_file = CACHE_DIR / f"book-{url_hash}.json"

    # Check local cache first
    if cache_file.exists() and metadata_file.exists():

        html = cache_file.read_bytes()

        metadata = json.loads(
            metadata_file.read_text(encoding="utf-8")
        )

        RUN_STATS["cache_hits"] += 1

        return html, metadata["fetched_at"]

    # Try at most twice
    for attempt in range(2):

        if attempt == 0:
            time.sleep(REQUEST_DELAY)
        else:
            print("Retrying once after temporary failure...")
            time.sleep(1)

        try:
            response = requests.get(
                product_url,
                headers=HEADERS,
                timeout=TIMEOUT
            )

            # Retry server errors once
            if 500 <= response.status_code <= 599:

                if attempt == 0:
                    print(f"Server error: HTTP {response.status_code}")
                    continue

                print(f"Failed after retry: HTTP {response.status_code}")
                RUN_STATS["failed_pages"] += 1
                return None, None

            # Do not retry 403 or 404
            if response.status_code in (403, 404):
                print(f"Page rejected or missing: HTTP {response.status_code}")
                RUN_STATS["failed_pages"] += 1
                return None, None

            # Other unsuccessful responses
            if response.status_code != 200:
                print(f"Unexpected HTTP status: {response.status_code}")
                RUN_STATS["failed_pages"] += 1
                return None, None

            html = response.content

            fetched_at = (
                datetime.now(timezone.utc)
                .isoformat(timespec="seconds")
                .replace("+00:00", "Z")
            )

            cache_file.write_bytes(html)

            metadata_file.write_text(
                json.dumps({"fetched_at": fetched_at}, indent=2),
                encoding="utf-8"
            )

            RUN_STATS["pages_fetched"] += 1

            return html, fetched_at

        except requests.Timeout as error:

            print(f"Request timed out: {error}")

            if attempt == 1:
                RUN_STATS["failed_pages"] += 1
                return None, None

        except requests.RequestException as error:

            print(f"Request failed: {error}")
            RUN_STATS["failed_pages"] += 1
            return None, None

    return None, None


# ---------------------------------
# 6. EXTRACT RAW BOOK RECORD
# ---------------------------------

def extract_book_record(product_url, source_page):

    html, fetched_at = fetch_book_page(product_url)

    if html is None:
        return None

    soup = BeautifulSoup(html, "html.parser")

    # Target the product information area
    product = soup.select_one(".product_main")

    if product is None:
        print(f"Product information missing: {product_url}")
        return None

    # Extract title
    title_element = product.select_one("h1")

    title = (
        title_element.get_text(strip=True)
        if title_element else None
    )

    # Extract price
    price_element = product.select_one(".price_color")

    price_text = (
        price_element.get_text(strip=True)
        if price_element else None
    )

    # Extract availability
    availability_element = product.select_one(".availability")

    availability_text = (
        availability_element.get_text(" ", strip=True)
        if availability_element else None
    )

    # Extract star rating
    rating_element = product.select_one(".star-rating")

    rating_text = None

    if rating_element:
        classes = rating_element.get("class", [])
        rating_text = next(
            (item for item in classes if item != "star-rating"),
            None
        )

    # Extract description
    description_heading = soup.select_one("#product_description")

    description = None

    if description_heading:
        description_element = description_heading.find_next_sibling("p")

        if description_element:
            description = description_element.get_text(strip=True)

    # Return all eight raw fields
    record = {
        "title": title,
        "product_url": product_url,
        "price_text": price_text,
        "availability_text": availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page": source_page,
        "fetched_at": fetched_at
    }

    return record

# ---------------------------------
# NORMALIZE RAW BOOK DATA
# ---------------------------------

def normalize_book(raw):

    # Convert "£51.77" into 51.77
    price_string = raw["price_text"].replace("£", "").replace(",", "").strip()
    price_gbp = float(price_string)

    # Convert rating words into numbers
    rating_mapping = {
        "One": 1,
        "Two": 2,
        "Three": 3,
        "Four": 4,
        "Five": 5
    }

    rating = rating_mapping.get(raw["rating_text"])

    if rating is None:
        raise ValueError(
            f"Unknown book rating: {raw['rating_text']}"
        )

    return {
        **raw,
        "price_gbp": price_gbp,
        "rating": rating
    }


# ---------------------------------
# VALIDATE BOOK DATA
# ---------------------------------

def validate_book(data):

    # Check that URLs are absolute HTTPS URLs
    for field in ["product_url", "source_page"]:
        value = data[field]
        parsed = urlparse(value)

        if parsed.scheme != "https" or not parsed.netloc:
            raise ValueError(
                f"{field} must be an absolute HTTPS URL"
            )

    # Validate data against the Pydantic schema
    return BookRecord(**data)


# ---------------------------------
# SAVE JSON OUTPUT
# ---------------------------------

OUTPUT_DIR = PROJECT_DIR / "output"


def save_results(valid_records, errors):

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    books_file = OUTPUT_DIR / "books.json"
    errors_file = OUTPUT_DIR / "errors.json"

    # Save valid records
    books_file.write_text(
        json.dumps(
            valid_records,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    # Save failed records and their reasons
    errors_file.write_text(
        json.dumps(
            errors,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    print(f"\nSaved valid records: {len(valid_records)}")
    print(f"Saved errors: {len(errors)}")
    print(f"Output directory: {OUTPUT_DIR}")

 

# ---------------------------------
# GENERATE RUN REPORT
# ---------------------------------

def save_run_report(start_time, start_timestamp):

    duration = round(time.time() - start_time, 2)

    report = {
        "started_at": start_timestamp,
        "duration_seconds": duration,
        "pages_fetched": RUN_STATS["pages_fetched"],
        "cache_hits": RUN_STATS["cache_hits"],
        "valid_records": RUN_STATS["valid_records"],
        "invalid_records": RUN_STATS["invalid_records"],
        "failed_pages": RUN_STATS["failed_pages"]
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    report_file = OUTPUT_DIR / "run-report.json"

    report_file.write_text(
        json.dumps(report, indent=4),
        encoding="utf-8"
    )

    print("\n--- RUN REPORT ---")
    print(json.dumps(report, indent=4))


# ---------------------------------
# PROCESS, NORMALIZE AND VALIDATE
# ---------------------------------


def extract_all_books():

    start_time = time.time()

    start_timestamp = (
        datetime.now(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z")
    )

    valid_records = []
    errors = []

    try:
        discovered_books = discover_catalogue()

        

        seen_urls = set()

        for index, (product_url, source_page) in enumerate(
            discovered_books, start=1
        ):

            print(f"Processing book {index}/{len(discovered_books)}")

            if product_url in seen_urls:
                continue

            seen_urls.add(product_url)

            # Fetch and extract separately
            raw = extract_book_record(
                product_url,
                source_page
            )

            # Failed page: log it and continue
            if raw is None:

                errors.append({
                    "product_url": product_url,
                    "reason": "Page fetch or extraction failed"
                })

                continue

            try:
                normalized = normalize_book(raw)

                validated = validate_book(normalized)

                valid_records.append(
                    validated.model_dump()
                    if hasattr(validated, "model_dump")
                    else validated.dict()
                )

            except Exception as error:

                RUN_STATS["invalid_records"] += 1

                errors.append({
                    "product_url": product_url,
                    "reason": str(error)
                })

        # Store results
        RUN_STATS["valid_records"] = len(valid_records)

        save_results(valid_records, errors)

    finally:
        # Report must be written even if processing raises an error
        save_run_report(start_time, start_timestamp)


# ---------------------------------
# 8. MAIN
# ---------------------------------

if __name__ == "__main__":
    extract_all_books()