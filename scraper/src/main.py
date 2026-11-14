
from pathlib import Path
from urllib.parse import urljoin
import time

import requests
from bs4 import BeautifulSoup

# Website configuration
BASE_URL = "https://books.toscrape.com/"

USER_AGENT = (
    "FlyRankInternshipA9/1.0 "
    "(+https://github.com/YOUR-USERNAME/YOUR-REPOSITORY)"
)

HEADERS = {
    "User-Agent": USER_AGENT
}

# Project paths
PROJECT_DIR = Path(__file__).resolve().parents[1]
CACHE_DIR = PROJECT_DIR / "cache"

# Request settings
TIMEOUT = 10
REQUEST_DELAY = 0.5


def get_page_html(url, page_number):
    """Read cached HTML or fetch and cache a catalogue page."""

    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    cache_file = CACHE_DIR / f"catalogue-page-{page_number}.html"

    # Use local cache if available
    if cache_file.exists():
        html = cache_file.read_bytes()

        print(f"CACHE HIT: page {page_number}")
        print(f"Response size: {len(html)} bytes")

        return html

    # Download only when cache is missing
    print(f"FETCH: page {page_number}")

    # Wait before making a real network request
    time.sleep(REQUEST_DELAY)

    try:
        response = requests.get(
            url,
            headers=HEADERS,
            timeout=TIMEOUT
        )

        # Check status before processing HTML
        if response.status_code != 200:
            print(
                f"Fetch failed for page {page_number}: "
                f"HTTP {response.status_code}"
            )
            return None

        html = response.content

        # Save downloaded HTML
        cache_file.write_bytes(html)

        print(f"Response size: {len(html)} bytes")
        print(f"Saved: {cache_file}")

        return html

    except requests.RequestException as error:
        print(f"Request failed for page {page_number}: {error}")
        return None


def discover_book_links(html, page_url):
    """Extract book links and convert them to absolute URLs."""

    soup = BeautifulSoup(html, "html.parser")

    book_urls = []

    # Find every book on the catalogue page
    for book in soup.select("article.product_pod h3 a"):
        href = book.get("href")

        if href:
            absolute_url = urljoin(page_url, href)
            book_urls.append(absolute_url)

    # Find the catalogue's own Next link
    next_link = soup.select_one("li.next a")

    next_url = None

    if next_link and next_link.get("href"):
        next_url = urljoin(page_url, next_link["href"])

    return book_urls, next_url


def discover_catalogue():
    """Discover books across the first three catalogue pages."""

    current_url = BASE_URL
    discovered_urls = []
    catalogue_pages = 0

    for page_number in range(1, 4):

        html = get_page_html(current_url, page_number)

        if html is None:
            print(f"Could not process catalogue page {page_number}")
            break

        book_urls, next_url = discover_book_links(
            html,
            current_url
        )

        discovered_urls.extend(book_urls)
        catalogue_pages += 1

        print(
            f"Page {page_number}: "
            f"discovered {len(book_urls)} book links"
        )

        # Stop if we have reached the third page
        if page_number == 3:
            break

        # Follow the website's Next link
        if not next_url:
            print("Next catalogue link not found. Stopping.")
            break

        current_url = next_url

    # Remove duplicate URLs while preserving order
    unique_urls = list(dict.fromkeys(discovered_urls))

    print("\n--- Discovery Report ---")
    print(f"catalogue_pages={catalogue_pages}")
    print(f"discovered={len(discovered_urls)}")
    print(f"unique_urls={len(unique_urls)}")


if __name__ == "__main__":
    discover_catalogue()
