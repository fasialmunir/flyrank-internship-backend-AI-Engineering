from pathlib import Path
import requests


# Website url
URL="https://books.toscrape.com/"

# Honest user-agent

USER_AGENT = (
    "FlyRankInternshipA9/1.0 "
    "(+https://github.com/fasialmunir/flyrank-internship-backend-AI-Engineering)"
)
# Project directories
PROJECT_DIR = Path(__file__).resolve().parents[1]
CACHE_DIR=PROJECT_DIR / "cache"
CACHE_FILE=CACHE_DIR / "catalogue-page-1.html"


def fetch_catalogue():
    # create cache directory if it doesn't exist
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    # check if cache file exists
    if CACHE_FILE.exists():
        html=CACHE_FILE.read_bytes()
        print("CACHE HIT")
        print(f"Response size: {len(html)} bytes")

        return html


    # download the catalogue page if cache file doesn't exist
    print("FETCH")
    
    headers={"User-Agent":USER_AGENT}
    try:
        response = requests.get(
            URL,
            headers=headers,
            timeout=10
        )
        
        # Check status before using the HTML
        if response.status_code != 200:
            print(f"Fetch failed: HTTP {response.status_code}")
            return None

        # Save the downloaded HTML
        html = response.content
        CACHE_FILE.write_bytes(html)

        print(f"Response size: {len(html)} bytes")
        print(f"Saved HTML to: {CACHE_FILE}")

        return html

    except requests.RequestException as e:
        print(f"Fetch failed: {e}")
        return None

if __name__=="__main__":
    fetch_catalogue()        