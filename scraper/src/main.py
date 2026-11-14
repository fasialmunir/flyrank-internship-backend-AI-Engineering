
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
# 7. PROCESS ALL 60 BOOKS
# ---------------------------------

def extract_all_books():

    discovered_books = discover_catalogue()

    records = []

    for index, (product_url, source_page) in enumerate(
        discovered_books, start=1
    ):

        print(f"Processing book {index}/{len(discovered_books)}")

        record = extract_book_record(
            product_url,
            source_page
        )

        if record is not None:
            records.append(record)

    # Print one complete raw record
    print("\n--- Sample Raw Record ---")

    if records:
        print(json.dumps(records[0], indent=4, ensure_ascii=False))
    else:
        print("No valid book records extracted.")

    print("\n--- Detail Extraction Report ---")
    print(f"detail_pages={len(records)}")


# ---------------------------------
# 8. MAIN
# ---------------------------------

if __name__ == "__main__":
    extract_all_books()