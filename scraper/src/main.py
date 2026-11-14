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

    if cache_file.exists():
        html = cache_file.read_bytes()

        print(f"CACHE HIT: page {page_number}")
        print(f"Response size: {len(html)} bytes")

        return html

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
            return None

        html = response.content
        cache_file.write_bytes(html)

        print(f"Response size: {len(html)} bytes")

        return html

    except requests.RequestException as error:
        print(f"Request failed: {error}")
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

    # Generate a unique cache filename
    url_hash = hashlib.sha256(
        product_url.encode("utf-8")
    ).hexdigest()

    cache_file = CACHE_DIR / f"book-{url_hash}.html"
    metadata_file = CACHE_DIR / f"book-{url_hash}.json"

    # Return cached HTML and original fetch time
    if cache_file.exists() and metadata_file.exists():

        html = cache_file.read_bytes()

        metadata = json.loads(
            metadata_file.read_text(encoding="utf-8")
        )

        return html, metadata["fetched_at"]

    # Make a polite network request
    time.sleep(REQUEST_DELAY)

    try:
        response = requests.get(
            product_url,
            headers=HEADERS,
            timeout=TIMEOUT
        )

        if response.status_code != 200:
            print(
                f"Book fetch failed: HTTP "
                f"{response.status_code} - {product_url}"
            )
            return None, None

        html = response.content

        # Record the actual fetch time in UTC
        fetched_at = (
            datetime.now(timezone.utc)
            .isoformat(timespec="seconds")
            .replace("+00:00", "Z")
        )

        # Save HTML and fetch-time metadata
        cache_file.write_bytes(html)

        metadata_file.write_text(
            json.dumps({"fetched_at": fetched_at}, indent=2),
            encoding="utf-8"
        )

        return html, fetched_at

    except requests.RequestException as error:

        print(f"Book request failed: {error}")

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
# 7. PROCESS ALL 60 BOOKS
# ---------------------------------


# ---------------------------------
# PROCESS, NORMALIZE AND VALIDATE
# ---------------------------------

def extract_all_books():

    discovered_books = discover_catalogue()

    valid_records = []
    errors = []

    # Track canonical product URLs to prevent duplicates
    seen_urls = set()

    for index, (product_url, source_page) in enumerate(
        discovered_books, start=1
    ):

        print(
            f"Processing book {index}/{len(discovered_books)}"
        )

        # Remove duplicate products
        if product_url in seen_urls:
            continue

        seen_urls.add(product_url)

        try:
            # Stage 3: Extract raw record
            raw = extract_book_record(
                product_url,
                source_page
            )

            if raw is None:
                raise ValueError("Could not extract book details")

            # Stage 4: Normalize raw values
            normalized = normalize_book(raw)

            # Stage 4: Validate against schema
            validated = validate_book(normalized)

            # Convert Pydantic model to dictionary
            valid_records.append(validated.dict())

        except Exception as error:

            errors.append({
                "product_url": product_url,
                "reason": str(error)
            })

    # Save the results
    save_results(valid_records, errors)

    print("\n--- Final Validation Report ---")
    print(f"total_records={len(valid_records)}")
    print(f"failed_records={len(errors)}")
    print(f"unique_records={len(valid_records)}")

    # Print one complete record
    if valid_records:
        print("\n--- Sample Valid Record ---")
        print(
            json.dumps(
                valid_records[0],
                indent=4,
                ensure_ascii=False
            )
        )


# ---------------------------------
# 8. MAIN
# ---------------------------------

if __name__ == "__main__":
    extract_all_books()